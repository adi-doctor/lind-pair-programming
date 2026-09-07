# Lind - The intelligent research platform.
# Mac Lee - Founding Engineer
# -----------------------------------------
import pandas
from tqdm import tqdm
import mysql.connector
from mysql.connector import Error as MySQLError
import time
from tabulate import tabulate
import pandas as pd

# Pair programming.
# 45 - 90 minutes.
# Local database variables -- MySQL.
local_database_host = 'localhost'
local_database_name = 'lind_pair_programming'
local_database_user = 'root'
local_database_password = 'BeachView2025@'
local_database_authentication_plugin = 'mysql_native_password'

class DataManager:
    df = pd.DataFrame()


def local_database_reachability_test():
    """
    Local database reachability test.
    """
    result = 0
    try:
        local_connection = mysql.connector.connect(host=local_database_host, database=local_database_name, user=local_database_user, password=local_database_password, auth_plugin=local_database_authentication_plugin)
        sql = "select "
        sql = sql + "connection_status_id,"
        sql = sql + "connection_status "
        sql = sql + "from connection_statuses;"
        local_cursor = local_connection.cursor()
        local_cursor.execute(sql)
        records = local_cursor.fetchall()
        for row in records:
            result = int(row[0])
        local_cursor.close()
        return result
    except MySQLError as e:
        print('(E) local_database_reachability_test error: ' + str(e))
        return result


def get_inner_join() -> pd.DataFrame:
    """
    An INNER JOIN combines rows from two tables only when there is a matching value in both tables based on a specified condition.
    """
    records = pd.DataFrame()
    try:
        local_connection = mysql.connector.connect(host=local_database_host, database=local_database_name, user=local_database_user, password=local_database_password, auth_plugin=local_database_authentication_plugin)
        sql_query = """
            select 
                e.emp_id, 
                e.name as employee_name, 
                d.dept_name,
                e.salary
            from employees e
            inner join departments d on e.dept_id = d.dept_id;
        """
        local_cursor = local_connection.cursor()
        local_cursor.execute(sql_query)
        records = local_cursor.fetchall()
    except MySQLError as e:
        print('(E) get_inner_join() error: ' + str(e))
    return records


def get_left_join() -> pd.DataFrame:
    """
    A LEFT JOIN (or LEFT OUTER JOIN) returns all records from the left table and the matched records from the right table. If there is no match on the right side, the result contains NULL (or NaN) for all columns coming from the right table.
    """
    records = pd.DataFrame()
    try:
        local_connection = mysql.connector.connect(host=local_database_host, database=local_database_name, user=local_database_user, password=local_database_password, auth_plugin=local_database_authentication_plugin)
        sql_query = """
            select 
                e.emp_id, 
                e.name as employee_name, 
                d.dept_name,
                e.salary
            from employees e
            left join departments d on e.dept_id = d.dept_id;
        """
        local_cursor = local_connection.cursor()
        local_cursor.execute(sql_query)
        records = local_cursor.fetchall()
    except MySQLError as e:
        print('(E) get_left_join() error: ' + str(e))
    return records


def get_right_join() -> pd.DataFrame:
    """
    Returns all departments, showing NULL/NaN for departments with no staff.
    A RIGHT JOIN (or RIGHT OUTER JOIN) returns all records from the right table and the matched records from the left table. If there is no match on the left side, the result contains NULL (or NaN) for all columns belonging to the left table.
    """
    records = pd.DataFrame()
    try:
        local_connection = mysql.connector.connect(host=local_database_host, database=local_database_name,
                                                   user=local_database_user, password=local_database_password,
                                                   auth_plugin=local_database_authentication_plugin)
        sql_query = """
            select 
                d.dept_id,
                d.dept_name,
                e.name as employee_name
            from employees e
            right join departments d on e.dept_id = d.dept_id;
        """
        local_cursor = local_connection.cursor()
        local_cursor.execute(sql_query)
        records = local_cursor.fetchall()
    except MySQLError as e:
        print('(E) get_right_join() error: ' + str(e))
    return records


def get_full_outer_join() -> pd.DataFrame:
    """Emulates a FULL OUTER JOIN by unioning LEFT and RIGHT joins."""
    records = pd.DataFrame()
    try:
        local_connection = mysql.connector.connect(host=local_database_host, database=local_database_name,
                                                   user=local_database_user, password=local_database_password,
                                                   auth_plugin=local_database_authentication_plugin)
        sql_query = """
            select e.name as employee_name, d.dept_name
            from employees e
            left join departments d on e.dept_id = d.dept_id
            union
            select e.name as employee_name, d.dept_name
            from employees e
            right join departments d on e.dept_id = d.dept_id;
        """
        local_cursor = local_connection.cursor()
        local_cursor.execute(sql_query)
        records = local_cursor.fetchall()
    except MySQLError as e:
        print('(E) get_full_outer_join() error: ' + str(e))
    return records


def get_self_join() -> pd.DataFrame:
    """Resolves hierarchical manager relationships within the employees table."""
    records = pd.DataFrame()
    try:
        local_connection = mysql.connector.connect(host=local_database_host, database=local_database_name,
                                                   user=local_database_user, password=local_database_password,
                                                   auth_plugin=local_database_authentication_plugin)
        sql_query = """
            select 
                emp.emp_id,
                emp.name as employee_name,
                coalesce(mgr.name, 'top manager / none') as manager_name
            from employees emp
            left join employees mgr on emp.manager_id = mgr.emp_id;
        """
        local_cursor = local_connection.cursor()
        local_cursor.execute(sql_query)
        records = local_cursor.fetchall()
    except MySQLError as e:
        print('(E) get_self_join() error: ' + str(e))
    return records


def get_cross_join() -> pd.DataFrame:
    """Produces the Cartesian product between employees and departments."""
    records = pd.DataFrame()
    try:
        local_connection = mysql.connector.connect(host=local_database_host, database=local_database_name,
                                                   user=local_database_user, password=local_database_password,
                                                   auth_plugin=local_database_authentication_plugin)
        sql_query = """
            select e.name as employee_name, d.dept_name
            from employees e
            cross join departments d
            order by e.name, d.dept_name;
        """
        local_cursor = local_connection.cursor()
        local_cursor.execute(sql_query)
        records = local_cursor.fetchall()
    except MySQLError as e:
        print('(E) get_cross_join() error: ' + str(e))
    return records


def get_anti_join_departments() -> pd.DataFrame:
    """Returns departments that have zero employees assigned."""
    records = pd.DataFrame()
    try:
        local_connection = mysql.connector.connect(host=local_database_host, database=local_database_name,
                                                   user=local_database_user, password=local_database_password,
                                                   auth_plugin=local_database_authentication_plugin)
        sql_query = """
            select d.dept_id, d.dept_name
            from departments d
            left join employees e on d.dept_id = e.dept_id
            where e.emp_id is null;
        """
        local_cursor = local_connection.cursor()
        local_cursor.execute(sql_query)
        records = local_cursor.fetchall()
    except MySQLError as e:
        print('(E) get_anti_join_departments() error: ' + str(e))
    return records


def get_multi_table_join() -> pd.DataFrame:
    """Joins employees, departments, and assigned projects."""
    records = pd.DataFrame()
    try:
        local_connection = mysql.connector.connect(host=local_database_host, database=local_database_name,
                                                   user=local_database_user, password=local_database_password,
                                                   auth_plugin=local_database_authentication_plugin)
        sql_query = """
            select 
                e.name as employee_name,
                d.dept_name,
                p.project_name
            from employees e
            inner join departments d on e.dept_id = d.dept_id
            inner join projects p on e.emp_id = p.emp_id;
        """
        local_cursor = local_connection.cursor()
        local_cursor.execute(sql_query)
        records = local_cursor.fetchall()
    except MySQLError as e:
        print('(E) get_multi_table_join() error: ' + str(e))
    return records


def get_group_by_having() -> pd.DataFrame:
    """Groups departments, calculates payroll stats, and filters via HAVING."""
    records = pd.DataFrame()
    try:
        local_connection = mysql.connector.connect(host=local_database_host, database=local_database_name,
                                                   user=local_database_user, password=local_database_password,
                                                   auth_plugin=local_database_authentication_plugin)
        sql_query = """
            select 
                d.dept_name,
                count(e.emp_id) as employee_count,
                round(avg(e.salary), 2) as average_salary,
                round(sum(e.salary), 2) as total_payroll
            from departments d
            inner join employees e on d.dept_id = e.dept_id
            group by d.dept_id, d.dept_name
            having count(e.emp_id) >= 2 and avg(e.salary) > 75000.00;
        """
        local_cursor = local_connection.cursor()
        local_cursor.execute(sql_query)
        records = local_cursor.fetchall()
    except MySQLError as e:
        print('(E) get_group_by_having() error: ' + str(e))
    return records


if __name__ == '__main__':
    local_database_reachable = local_database_reachability_test()
    if local_database_reachable == 0:
        print('Local database is not reachable.')
        exit()
    else:
        print('Local database is reachable.')

        print('Inner Join:')
        DataManager = get_inner_join()
        print(tabulate(DataManager, headers='keys', tablefmt='grid'))

        print('Left Join:')
        DataManager = get_left_join()
        print(tabulate(DataManager, headers='keys', tablefmt='grid'))

        print('Right Join:')
        DataManager = get_right_join()
        print(tabulate(DataManager, headers='keys', tablefmt='grid'))

        print('Full Outer Join:')
        DataManager = get_full_outer_join()
        print(tabulate(DataManager, headers='keys', tablefmt='grid'))

        print('Self Join:')
        DataManager = get_self_join()
        print(tabulate(DataManager, headers='keys', tablefmt='grid'))

        print('Cross Join:')
        DataManager = get_cross_join()
        print(tabulate(DataManager, headers='keys', tablefmt='grid'))

        print('Anti Join Departments:')
        DataManager = get_anti_join_departments()
        print(tabulate(DataManager, headers='keys', tablefmt='grid'))

        print('Multi-Table Join:')
        DataManager = get_multi_table_join()
        print(tabulate(DataManager, headers='keys', tablefmt='grid'))

        print('Group By Having:')
        DataManager = get_group_by_having()
        print(tabulate(DataManager, headers='keys', tablefmt='grid'))

