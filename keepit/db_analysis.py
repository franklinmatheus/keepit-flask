from keepit.db import get_db

def get_balance(id_user: int):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    select_query = ('''SELECT (receitas_comuns.total + receitas_incomuns.total) - (despesas_comuns.total + despesas_incomuns.total) saldo FROM 
    (SELECT COALESCE(SUM(keepit.pagamento_recurso.valor),0) total FROM 
        (((keepit.recurso JOIN keepit.despesa ON keepit.recurso.id_recurso = keepit.despesa.id_recurso) 
        JOIN keepit.pagamento_recurso ON keepit.pagamento_recurso.id_recurso = keepit.recurso.id_recurso)
        JOIN keepit.despesa_comum ON keepit.despesa.id_despesa = keepit.despesa_comum.id_despesa)
        WHERE keepit.pagamento_recurso.data_pagamento IS NOT NULL
        AND keepit.recurso.id_usuario=%s) AS despesas_comuns,
    (SELECT COALESCE(SUM(keepit.pagamento_recurso.valor),0) total FROM 
        (((keepit.recurso JOIN keepit.despesa ON keepit.recurso.id_recurso=keepit.despesa.id_recurso) 
        JOIN keepit.pagamento_recurso ON keepit.pagamento_recurso.id_recurso = keepit.recurso.id_recurso)
        JOIN keepit.despesa_incomum ON keepit.despesa.id_despesa = keepit.despesa_incomum.id_despesa)
        WHERE keepit.pagamento_recurso.data_pagamento IS NOT NULL
        AND keepit.recurso.data_cancelamento IS NOT NULL
        AND keepit.recurso.id_usuario=%s) AS despesas_incomuns,
    (SELECT COALESCE(SUM(keepit.pagamento_recurso.valor),0) total FROM 
        (((keepit.recurso JOIN keepit.receita ON keepit.recurso.id_recurso=keepit.receita.id_recurso) 
        JOIN keepit.pagamento_recurso ON keepit.pagamento_recurso.id_recurso = keepit.recurso.id_recurso)
        JOIN keepit.receita_comum ON keepit.receita.id_receita = keepit.receita_comum.id_receita)
        WHERE keepit.pagamento_recurso.data_pagamento IS NOT NULL
        AND keepit.recurso.id_usuario=%s) AS receitas_comuns,
    (SELECT COALESCE(SUM(keepit.pagamento_recurso.valor),0) total FROM 
        (((keepit.recurso JOIN keepit.receita ON keepit.recurso.id_recurso=keepit.receita.id_recurso) 
        JOIN keepit.pagamento_recurso ON keepit.pagamento_recurso.id_recurso = keepit.recurso.id_recurso)
        JOIN keepit.receita_incomum ON keepit.receita.id_receita = keepit.receita_incomum.id_receita)
        WHERE keepit.pagamento_recurso.data_pagamento IS NOT NULL
        AND keepit.recurso.data_cancelamento IS NOT NULL
        AND keepit.recurso.id_usuario=%s) AS receitas_incomuns
    ''')

    select_data = (id_user,id_user,id_user,id_user)
    cursor.execute(select_query,select_data)
    result = cursor.fetchone()

    cursor.close()
    db.close()

    return result['saldo']

def get_expenses_info(id_user: int, month: int, year: int):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    info = {'comum':{'desatualizadas':0,'quantidade':0,'total':0}
        ,'incomum':{'quantidade':0,'total':0}}

    select_query = ('''SELECT COUNT(DISTINCT(keepit.recurso.id_recurso)) quantidade,
        SUM(keepit.pagamento_recurso.valor) total FROM 
	    (((keepit.recurso JOIN keepit.despesa ON keepit.recurso.id_recurso=keepit.despesa.id_recurso) 
        JOIN keepit.despesa_comum ON keepit.despesa.id_despesa=keepit.despesa_comum.id_despesa) 
        JOIN keepit.pagamento_recurso ON keepit.pagamento_recurso.id_recurso = keepit.recurso.id_recurso)
    WHERE keepit.recurso.id_usuario=%s and keepit.pagamento_recurso.data_pagamento IS NOT NULL
    AND MONTH(keepit.pagamento_recurso.data_pagamento) = %s AND YEAR(keepit.pagamento_recurso.data_pagamento) = %s
    GROUP BY keepit.recurso.id_usuario
    ''')
    select_data = (id_user,month,year)
    cursor.execute(select_query,select_data)
    quantity_info = cursor.fetchone()
    if quantity_info is not None:
        info['comum']['quantidade'] = quantity_info['quantidade']
        info['comum']['total'] = quantity_info['total']

    select_query = ('''SELECT COUNT(*) desatualizadas FROM 
	    ((keepit.recurso JOIN keepit.despesa ON keepit.recurso.id_recurso=keepit.despesa.id_recurso) 
        JOIN keepit.despesa_comum ON keepit.despesa.id_despesa=keepit.despesa_comum.id_despesa)
    WHERE keepit.recurso.id_usuario=%s AND keepit.despesa_comum.status=0
    ''')
    select_data = (id_user,)
    cursor.execute(select_query,select_data)
    late_info = cursor.fetchone()
    if late_info is not None:
        info['comum']['desatualizadas'] = late_info['desatualizadas']

    select_query = ('''SELECT COUNT(DISTINCT(keepit.recurso.id_recurso)) quantidade,
    SUM(keepit.pagamento_recurso.valor) total FROM 
	    (((keepit.recurso JOIN keepit.despesa ON keepit.recurso.id_recurso=keepit.despesa.id_recurso) 
        JOIN keepit.despesa_incomum ON keepit.despesa.id_despesa=keepit.despesa_incomum.id_despesa) 
        JOIN keepit.pagamento_recurso ON keepit.pagamento_recurso.id_recurso = keepit.recurso.id_recurso)
    WHERE keepit.recurso.id_usuario=%s and keepit.pagamento_recurso.data_pagamento IS NOT NULL
    AND keepit.recurso.data_cancelamento IS NULL
    AND MONTH(keepit.pagamento_recurso.data_pagamento) = %s AND YEAR(keepit.pagamento_recurso.data_pagamento) = %s
    GROUP BY keepit.recurso.id_usuario
    ''')
    select_data = (id_user,month,year)
    cursor.execute(select_query,select_data)
    quantity_info = cursor.fetchone()
    if quantity_info is not None:
        info['incomum']['quantidade'] = quantity_info['quantidade']
        info['incomum']['total'] = quantity_info['total']

    cursor.close()
    db.close()

    return info

def get_revenues_info(id_user: int, month: int, year: int):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    info = {'comum':{'desatualizadas':0,'quantidade':0,'total':0}
        ,'incomum':{'quantidade':0,'total':0}}

    select_query = ('''SELECT COUNT(DISTINCT(keepit.recurso.id_recurso)) quantidade,
    SUM(keepit.pagamento_recurso.valor) total FROM 
	    (((keepit.recurso JOIN keepit.receita ON keepit.recurso.id_recurso=keepit.receita.id_recurso) 
        JOIN keepit.receita_comum ON keepit.receita.id_receita=keepit.receita_comum.id_receita) 
        JOIN keepit.pagamento_recurso ON keepit.pagamento_recurso.id_recurso = keepit.recurso.id_recurso)
    WHERE keepit.recurso.id_usuario=%s and keepit.pagamento_recurso.data_pagamento IS NOT NULL
    AND MONTH(keepit.pagamento_recurso.data_pagamento) = %s AND YEAR(keepit.pagamento_recurso.data_pagamento) = %s
    GROUP BY keepit.recurso.id_usuario
    ''')
    select_data = (id_user,month,year)
    cursor.execute(select_query,select_data)
    quantity_info = cursor.fetchone()
    if quantity_info is not None:
        info['comum']['quantidade'] = quantity_info['quantidade']
        info['comum']['total'] = quantity_info['total']

    select_query = ('''SELECT COUNT(*) desatualizadas FROM 
	    ((keepit.recurso JOIN keepit.receita ON keepit.recurso.id_recurso=keepit.receita.id_recurso) 
        JOIN keepit.receita_comum ON keepit.receita.id_receita=keepit.receita_comum.id_receita)
    WHERE keepit.recurso.id_usuario=%s AND keepit.receita_comum.status=0
    ''')
    select_data = (id_user,)
    cursor.execute(select_query,select_data)
    late_info = cursor.fetchone()
    if late_info is not None:
        info['comum']['desatualizadas'] = late_info['desatualizadas']
        
    select_query = ('''SELECT COUNT(DISTINCT(keepit.recurso.id_recurso)) quantidade,
    SUM(keepit.pagamento_recurso.valor) total FROM 
	    (((keepit.recurso JOIN keepit.receita ON keepit.recurso.id_recurso=keepit.receita.id_recurso) 
        JOIN keepit.receita_incomum ON keepit.receita.id_receita=keepit.receita_incomum.id_receita) 
        JOIN keepit.pagamento_recurso ON keepit.pagamento_recurso.id_recurso = keepit.recurso.id_recurso)
    WHERE keepit.recurso.id_usuario=%s and keepit.pagamento_recurso.data_pagamento IS NOT NULL
    AND MONTH(keepit.pagamento_recurso.data_pagamento) = %s AND YEAR(keepit.pagamento_recurso.data_pagamento) = %s
    AND keepit.recurso.data_cancelamento IS NULL
    GROUP BY keepit.recurso.id_usuario
    ''')
    select_data = (id_user,month,year)
    cursor.execute(select_query,select_data)
    quantity_info = cursor.fetchone()
    if quantity_info is not None:
        info['incomum']['quantidade'] = quantity_info['quantidade']
        info['incomum']['total'] = quantity_info['total']

    cursor.close()
    db.close()

    return info

def get_total_expenses_by_day(id_user: int):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    select_query = ('''SELECT despesas.data_pagamento, COUNT(*) quantidade, SUM(despesas.valor) total FROM (
        (SELECT keepit.pagamento_recurso.data_pagamento, keepit.pagamento_recurso.valor FROM 
            (((keepit.recurso JOIN keepit.despesa ON keepit.recurso.id_recurso = keepit.despesa.id_recurso) 
            JOIN keepit.pagamento_recurso ON keepit.pagamento_recurso.id_recurso = keepit.recurso.id_recurso)
            JOIN keepit.despesa_comum ON keepit.despesa.id_despesa = keepit.despesa_comum.id_despesa)
        WHERE keepit.recurso.id_usuario=%s 
        AND keepit.pagamento_recurso.data_pagamento IS NOT NULL)
    UNION
        (SELECT keepit.pagamento_recurso.data_pagamento, keepit.pagamento_recurso.valor FROM 
            (((keepit.recurso JOIN keepit.despesa ON keepit.recurso.id_recurso = keepit.despesa.id_recurso) 
            JOIN keepit.pagamento_recurso ON keepit.pagamento_recurso.id_recurso = keepit.recurso.id_recurso)
            JOIN keepit.despesa_incomum ON keepit.despesa.id_despesa = keepit.despesa_incomum.id_despesa)
        WHERE keepit.recurso.id_usuario=%s 
        AND keepit.pagamento_recurso.data_pagamento IS NOT NULL
        AND keepit.recurso.data_cancelamento IS NULL)) despesas
    GROUP BY despesas.data_pagamento
    ''')
    select_data = (id_user,id_user)
    cursor.execute(select_query,select_data)
    results = cursor.fetchall()
    
    cursor.close()
    db.close()

    return results

def get_total_revenues_by_day(id_user: int):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    select_query = ('''SELECT receitas.data_pagamento, COUNT(*) quantidade, SUM(receitas.valor) total FROM (
        (SELECT keepit.pagamento_recurso.data_pagamento, keepit.pagamento_recurso.valor FROM 
            (((keepit.recurso JOIN keepit.receita ON keepit.recurso.id_recurso = keepit.receita.id_recurso) 
            JOIN keepit.pagamento_recurso ON keepit.pagamento_recurso.id_recurso = keepit.recurso.id_recurso)
            JOIN keepit.receita_comum ON keepit.receita.id_receita = keepit.receita_comum.id_receita)
        WHERE keepit.recurso.id_usuario=%s 
        AND keepit.pagamento_recurso.data_pagamento IS NOT NULL)
    UNION
        (SELECT keepit.pagamento_recurso.data_pagamento, keepit.pagamento_recurso.valor FROM 
            (((keepit.recurso JOIN keepit.receita ON keepit.recurso.id_recurso = keepit.receita.id_recurso) 
            JOIN keepit.pagamento_recurso ON keepit.pagamento_recurso.id_recurso = keepit.recurso.id_recurso)
            JOIN keepit.receita_incomum ON keepit.receita.id_receita = keepit.receita_incomum.id_receita)
        WHERE keepit.recurso.id_usuario=%s 
        AND keepit.pagamento_recurso.data_pagamento IS NOT NULL
        AND keepit.recurso.data_cancelamento IS NULL)) receitas
    GROUP BY receitas.data_pagamento
    ''')
    select_data = (id_user,id_user)
    cursor.execute(select_query,select_data)
    results = cursor.fetchall()
    
    cursor.close()
    db.close()

    return results

def get_total_expenses_by_month(id_user: int, year: int):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    select_query = ('''SELECT * FROM 
            (SELECT MONTH(keepit.pagamento_recurso.data_pagamento) mes_comum, SUM(keepit.pagamento_recurso.valor) total_comum FROM 
            (((keepit.recurso JOIN keepit.despesa ON keepit.recurso.id_recurso = keepit.despesa.id_recurso) 
            JOIN keepit.pagamento_recurso ON keepit.pagamento_recurso.id_recurso = keepit.recurso.id_recurso)
            JOIN keepit.despesa_comum ON keepit.despesa.id_despesa = keepit.despesa_comum.id_despesa)
            WHERE keepit.recurso.id_usuario=%s AND keepit.pagamento_recurso.data_pagamento IS NOT NULL
            AND YEAR(keepit.pagamento_recurso.data_pagamento) = %s
            GROUP BY MONTH(keepit.pagamento_recurso.data_pagamento)) despesas_comuns
        RIGHT JOIN  
            (SELECT MONTH(keepit.pagamento_recurso.data_pagamento) mes_incomum, SUM(keepit.pagamento_recurso.valor) total_incomum FROM 
            (((keepit.recurso JOIN keepit.despesa ON keepit.recurso.id_recurso=keepit.despesa.id_recurso) 
            JOIN keepit.pagamento_recurso ON keepit.pagamento_recurso.id_recurso = keepit.recurso.id_recurso)
            JOIN keepit.despesa_incomum ON keepit.despesa.id_despesa = keepit.despesa_incomum.id_despesa)
            WHERE keepit.pagamento_recurso.data_pagamento IS NOT NULL
            AND keepit.recurso.data_cancelamento IS NULL
            AND keepit.recurso.id_usuario=%s
            AND YEAR(keepit.pagamento_recurso.data_pagamento) = %s
            GROUP BY MONTH(keepit.pagamento_recurso.data_pagamento)) despesas_incomuns
        ON despesas_comuns.mes_comum = despesas_incomuns.mes_incomum
    UNION 
        SELECT * FROM 
            (SELECT MONTH(keepit.pagamento_recurso.data_pagamento) mes_comum, SUM(keepit.pagamento_recurso.valor) total_comum FROM 
            (((keepit.recurso JOIN keepit.despesa ON keepit.recurso.id_recurso = keepit.despesa.id_recurso) 
            JOIN keepit.pagamento_recurso ON keepit.pagamento_recurso.id_recurso = keepit.recurso.id_recurso)
            JOIN keepit.despesa_comum ON keepit.despesa.id_despesa = keepit.despesa_comum.id_despesa)
            WHERE keepit.recurso.id_usuario=%s AND keepit.pagamento_recurso.data_pagamento IS NOT NULL
            AND YEAR(keepit.pagamento_recurso.data_pagamento) = %s
            GROUP BY MONTH(keepit.pagamento_recurso.data_pagamento)) despesas_comuns
        LEFT JOIN 
            (SELECT MONTH(keepit.pagamento_recurso.data_pagamento) mes_incomum, SUM(keepit.pagamento_recurso.valor) total_incomum FROM 
            (((keepit.recurso JOIN keepit.despesa ON keepit.recurso.id_recurso=keepit.despesa.id_recurso) 
            JOIN keepit.pagamento_recurso ON keepit.pagamento_recurso.id_recurso = keepit.recurso.id_recurso)
            JOIN keepit.despesa_incomum ON keepit.despesa.id_despesa = keepit.despesa_incomum.id_despesa)
            WHERE keepit.pagamento_recurso.data_pagamento IS NOT NULL
            AND keepit.recurso.data_cancelamento IS NULL
            AND keepit.recurso.id_usuario=%s
            AND YEAR(keepit.pagamento_recurso.data_pagamento) = %s
            GROUP BY MONTH(keepit.pagamento_recurso.data_pagamento)) despesas_incomuns
        ON despesas_comuns.mes_comum = despesas_incomuns.mes_incomum
    ''')
    select_data = (id_user,year,id_user,year,id_user,year,id_user,year)
    cursor.execute(select_query,select_data)
    results = cursor.fetchall()

    cursor.close()
    db.close()

    for result in results:
        if result['total_comum'] is not None and result['total_incomum'] is not None:
            result['total'] = result['total_comum'] + result['total_incomum']
        elif result['total_comum'] is not None:
            result['total'] = result['total_comum']
        elif result['total_incomum'] is not None:
            result['total'] = result['total_incomum']

        if result['mes_comum'] is not None:
            result['mes'] = result['mes_comum']
        elif result['mes_incomum'] is not None:
            result['mes'] = result['mes_incomum']

        del result['total_incomum']
        del result['mes_incomum']
        del result['total_comum']
        del result['mes_comum']

    return results

def get_total_revenues_by_month(id_user: int, year: int):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    select_query = ('''SELECT * FROM 
            (SELECT MONTH(keepit.pagamento_recurso.data_pagamento) mes_comum, SUM(keepit.pagamento_recurso.valor) total_comum FROM 
            (((keepit.recurso JOIN keepit.receita ON keepit.recurso.id_recurso = keepit.receita.id_recurso) 
            JOIN keepit.pagamento_recurso ON keepit.pagamento_recurso.id_recurso = keepit.recurso.id_recurso)
            JOIN keepit.receita_comum ON keepit.receita.id_receita = keepit.receita_comum.id_receita)
            WHERE keepit.recurso.id_usuario=%s AND keepit.pagamento_recurso.data_pagamento IS NOT NULL
            AND YEAR(keepit.pagamento_recurso.data_pagamento) = %s
            GROUP BY MONTH(keepit.pagamento_recurso.data_pagamento)) receitas_comuns
        RIGHT JOIN  
            (SELECT MONTH(keepit.pagamento_recurso.data_pagamento) mes_incomum, SUM(keepit.pagamento_recurso.valor) total_incomum FROM 
            (((keepit.recurso JOIN keepit.receita ON keepit.recurso.id_recurso=keepit.receita.id_recurso) 
            JOIN keepit.pagamento_recurso ON keepit.pagamento_recurso.id_recurso = keepit.recurso.id_recurso)
            JOIN keepit.receita_incomum ON keepit.receita.id_receita = keepit.receita_incomum.id_receita)
            WHERE keepit.pagamento_recurso.data_pagamento IS NOT NULL
            AND keepit.recurso.data_cancelamento IS NULL
            AND keepit.recurso.id_usuario=%s
            AND YEAR(keepit.pagamento_recurso.data_pagamento) = %s
            GROUP BY MONTH(keepit.pagamento_recurso.data_pagamento)) receitas_incomuns
        ON receitas_comuns.mes_comum = receitas_incomuns.mes_incomum
    UNION 
        SELECT * FROM 
            (SELECT MONTH(keepit.pagamento_recurso.data_pagamento) mes_comum, SUM(keepit.pagamento_recurso.valor) total_comum FROM 
            (((keepit.recurso JOIN keepit.receita ON keepit.recurso.id_recurso = keepit.receita.id_recurso) 
            JOIN keepit.pagamento_recurso ON keepit.pagamento_recurso.id_recurso = keepit.recurso.id_recurso)
            JOIN keepit.receita_comum ON keepit.receita.id_receita = keepit.receita_comum.id_receita)
            WHERE keepit.recurso.id_usuario=%s AND keepit.pagamento_recurso.data_pagamento IS NOT NULL
            AND YEAR(keepit.pagamento_recurso.data_pagamento) = %s
            GROUP BY MONTH(keepit.pagamento_recurso.data_pagamento)) receitas_comuns
        LEFT JOIN 
            (SELECT MONTH(keepit.pagamento_recurso.data_pagamento) mes_incomum, SUM(keepit.pagamento_recurso.valor) total_incomum FROM 
            (((keepit.recurso JOIN keepit.receita ON keepit.recurso.id_recurso=keepit.receita.id_recurso) 
            JOIN keepit.pagamento_recurso ON keepit.pagamento_recurso.id_recurso = keepit.recurso.id_recurso)
            JOIN keepit.receita_incomum ON keepit.receita.id_receita = keepit.receita_incomum.id_receita)
            WHERE keepit.pagamento_recurso.data_pagamento IS NOT NULL
            AND keepit.recurso.data_cancelamento IS NULL
            AND keepit.recurso.id_usuario=%s
            AND YEAR(keepit.pagamento_recurso.data_pagamento) = %s
            GROUP BY MONTH(keepit.pagamento_recurso.data_pagamento)) receitas_incomuns
        ON receitas_comuns.mes_comum = receitas_incomuns.mes_incomum
    ''')
    select_data = (id_user,year,id_user,year,id_user,year,id_user,year)
    cursor.execute(select_query,select_data)
    results = cursor.fetchall()

    cursor.close()
    db.close()

    for result in results:
        if result['total_comum'] is not None and result['total_incomum'] is not None:
            result['total'] = result['total_comum'] + result['total_incomum']
        elif result['total_comum'] is not None:
            result['total'] = result['total_comum']
        elif result['total_incomum'] is not None:
            result['total'] = result['total_incomum']

        if result['mes_comum'] is not None:
            result['mes'] = result['mes_comum']
        elif result['mes_incomum'] is not None:
            result['mes'] = result['mes_incomum']

        del result['total_incomum']
        del result['mes_incomum']
        del result['total_comum']
        del result['mes_comum']

    return results