"""********************************************************************"""
"""                                                                    """
"""   [files] FileReader.py                                            """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 14/08/2021 05:44:22                                     """
"""   Updated: 04/09/2021 04:40:42                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import csv

def ReadFile(path):
    lines = []
    
    try:
        file = open(path, mode='r', encoding='utf-8')
    except FileNotFoundError:
        return None
    except Exception:
        return None
        
    try:
        for line in file.readlines():
            lines.append(line.strip())
    except Exception:
        return None
        
    file.close()
    return (len(lines), lines)

def ReadCSV(path):
    rows = []
    
    try:
        file = open(path, mode='r', encoding='utf-8')
    except FileNotFoundError:
        return None
    except Exception:
        return None
        
    lines = csv.DictReader(file, delimiter=',')
    
    for line in lines:
        rows.append(line)

    file.close()
    return (rows)
