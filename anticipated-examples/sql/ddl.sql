# database schema and setup.
# --------------------------
create database lind_pair_programming;
use lind_pair_programming;

-- reachability test.
create table connection_statuses (
    connection_status_id int auto_increment unique primary key not null,
    connection_status varchar(100) not null,
    active_indicator int not null default 1
);
insert into connection_statuses (
    connection_status
) values (
     'Active'
);
select * from connection_statuses;

-- clean up child tables before parent tables to avoid foreign key errors
drop table if exists projects;
drop table if exists employees;
drop table if exists departments;

-- 1. departments table
create table departments (
    dept_id int auto_increment,
    dept_name varchar(50) not null,
    primary key (dept_id)
) engine=innodb;

-- 2. employees table
-- uses auto_increment primary key and references both departments and itself
create table employees (
    emp_id int auto_increment,
    name varchar(50) not null,
    dept_id int null,
    manager_id int null,
    primary key (emp_id),
    constraint fk_emp_dept
        foreign key (dept_id) references departments(dept_id)
        on delete set null,
    constraint fk_emp_manager
        foreign key (manager_id) references employees(emp_id)
        on delete set null
) engine=innodb;

-- 3. projects table
create table projects (
    project_id int auto_increment,
    project_name varchar(50) not null,
    emp_id int null,
    primary key (project_id),
    constraint fk_proj_emp
        foreign key (emp_id) references employees(emp_id)
        on delete set null
) engine=innodb;


-- =============================================================
-- 2. sample data insertion
-- ids are omitted so auto_increment assigns them starting at 1
-- =============================================================

-- departments: ids will be generated as 1, 2, 3, 4
insert into departments (dept_name) values
    ('engineering'), -- dept_id: 1
    ('design'),      -- dept_id: 2
    ('marketing'),   -- dept_id: 3
    ('finance');     -- dept_id: 4 (no employees assigned)

-- employees: insert top-level manager first so subordinates can reference manager_id
insert into employees (name, dept_id, manager_id) values
    ('alice', 1, null); -- emp_id: 1 (engineering, head manager)

-- now insert employees referencing alice (emp_id: 1)
insert into employees (name, dept_id, manager_id) values
    ('bob',     1,    1),    -- emp_id: 2 (engineering, reports to alice)
    ('charlie', 2,    1),    -- emp_id: 3 (design, reports to alice)
    ('david',   null, 2);    -- emp_id: 4 (contractor: no department, reports to bob)

-- projects: assigned to generated emp_ids
insert into projects (project_name, emp_id) values
    ('alpha portal', 1),    -- managed by alice
    ('beta ui',      3),    -- managed by charlie
    ('internal tool', null); -- unassigned project


-- ++++++

-- Add salary column if running on the existing table
alter table employees add column salary decimal(10, 2);
-- Update sample rows with salary figures
update employees set salary = 95000.00 where emp_id = 1; -- alice (engineering)
update employees set salary = 80000.00 where emp_id = 2; -- bob (engineering)
update employees set salary = 85000.00 where emp_id = 3; -- charlie (design)
update employees set salary = 60000.00 where emp_id = 4; -- david (no dept)

    -- Insert extra records to create richer groupings
insert into employees (name, dept_id, manager_id, salary) values
    ('eva',   1, 1, 75000.00), -- engineering
    ('frank', 2, 1, 70000.00); -- design

-- =============================================================
-- 3. inner join
-- returns records with matching keys in both tables.
-- excludes david (dept_id = null) and finance (no employees).
-- =============================================================
select
    e.emp_id,
    e.name as employee_name,
    d.dept_id,
    d.dept_name
from employees e
inner join departments d on e.dept_id = d.dept_id;

-- =============================================================
-- 4. left (outer) join
-- returns all employees; david displays with dept_name = null.
-- =============================================================
select
    e.emp_id,
    e.name as employee_name,
    d.dept_name
from employees e
left join departments d on e.dept_id = d.dept_id;

-- =============================================================
-- 5. right (outer) join
-- returns all departments; finance displays with employee = null.
-- =============================================================
select
    e.name as employee_name,
    d.dept_id,
    d.dept_name
from employees e
right join departments d on e.dept_id = d.dept_id;

-- =============================================================
-- 6. full outer join (emulated via union)
-- combines left and right joins to preserve non-matching rows on both sides.
-- =============================================================
select
    e.name as employee_name,
    d.dept_name
from employees e
left join departments d on e.dept_id = d.dept_id

union

select
    e.name as employee_name,
    d.dept_name
from employees e
right join departments d on e.dept_id = d.dept_id;

-- =============================================================
-- 7. self join
-- maps employee rows to their manager within the same table.
-- =============================================================
select
    emp.emp_id,
    emp.name as employee_name,
    coalesce(mgr.name, 'top manager / none') as manager_name
from employees emp
left join employees mgr on emp.manager_id = mgr.emp_id;

-- =============================================================
-- 8. cross join (cartesian product)
-- pairs every employee with every department (4 employees * 4 depts = 16 rows).
-- =============================================================
select
    e.name as employee_name,
    d.dept_name
from employees e
cross join departments d
order by e.name, d.dept_name;

-- =============================================================
-- 9. anti-join (left join ... where right.key is null)
-- filters for orphaned/unlinked records.
-- =============================================================
-- departments with zero employees
select
    d.dept_id,
    d.dept_name
from departments d
left join employees e on d.dept_id = e.dept_id
where e.emp_id is null;

-- employees with no department assigned
select
    e.emp_id,
    e.name as unassigned_employee
from employees e
left join departments d on e.dept_id = d.dept_id
where d.dept_id is null;

-- =============================================================
-- 10. multi-table join
-- combines employees, their departments, and their assigned projects.
-- =============================================================
select
    e.name as employee_name,
    d.dept_name,
    p.project_name
from employees e
inner join departments d on e.dept_id = d.dept_id
inner join projects p on e.emp_id = p.emp_id;

-- Group by having

select
    d.dept_name,
    count(e.emp_id) as total_employees
from departments d
inner join employees e on d.dept_id = e.dept_id
group by d.dept_id, d.dept_name
having count(e.emp_id) > 1;

-- where, group by, having
select
    d.dept_name,
    count(e.emp_id) as eligible_employees,
    round(avg(e.salary), 2) as average_salary
from departments d
inner join employees e on d.dept_id = e.dept_id
where e.salary >= 72000.00            -- 1. pre-filter rows first
group by d.dept_id, d.dept_name        -- 2. group surviving records
having avg(e.salary) > 75000.00        -- 3. filter summary metrics
order by average_salary desc;          -- 4. sort results