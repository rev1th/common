
import sqlite3
import logging

logger = logging.Logger(__name__)

DATE_FORMAT = '%Y-%m-%d'

def fetch(query: str, filename: str, count: int = 0):
    connect = sqlite3.connect(f'data/{filename}')
    cursor = connect.cursor()
    try:
        exec_obj = cursor.execute(query)
        if count == 1:
            res = exec_obj.fetchone()
        elif count > 1:
            res = exec_obj.fetchmany(count)
        else:
            res = exec_obj.fetchall()
    except Exception as ex:
        raise RuntimeError(f'Fetch failed: {ex}')
    connect.close()
    return res

def modify(query: str, filename: str) -> bool:
    connect = sqlite3.connect(f'data/{filename}')
    cursor = connect.cursor()
    try:
        logger.error(f'modifying {filename}: {query}')
        cursor.execute(query)
        connect.commit()
    except Exception as ex:
        raise RuntimeError(f'Modify failed: {ex}')
    connect.close()
    return True

