from api.utils.bcra_client import get_bcra_data

LGD = 0.6


def situation_to_score(situation):

    mapping = {1: 850, 2: 700, 3: 550, 4: 400, 5: 300}

    return mapping.get(situation, 300)


def calculate_pd(score):

    if score >= 800:
        return 0.01
    elif score >= 700:
        return 0.03
    elif score >= 600:
        return 0.08
    elif score >= 500:
        return 0.18
    else:
        return 0.35


def calculate_period_debt(period):

    debt = 0

    for e in period.get("entidades", []):
        debt += int(e.get("monto", 0) or 0) * 1000

    return debt


def calculate_debt_trend(periods):

    if len(periods) < 6:
        return 0

    current_debt = calculate_period_debt(periods[0])
    past_debt = calculate_period_debt(periods[5])

    if past_debt <= 0:
        return 0

    trend = (current_debt - past_debt) / past_debt

    return trend


def trend_penalty(trend):

    if trend <= -0.40:
        return -40
    elif trend <= -0.10:
        return -20
    elif trend < 0.10:
        return 0
    elif trend < 0.40:
        return 40
    else:
        return 80


def analyze_bcra_data(bcra_data):

    periods = bcra_data.get("periodos", [])

    if not periods:
        return {
            "total_debt": 0,
            "entities": 0,
            "situation": 1,
            "days_late": 0,
            "legal_flags": False,
            "historical_worst": 1,
            "avg_days_late": 0,
            "stability_score": 1,
            "debt_trend": 0,
        }

    current_period = periods[0]
    entities = current_period.get("entidades", [])

    total_debt = 0
    entity_count = len(entities)
    worst_situation = 1
    max_days_late = 0
    legal_flags = False

    for e in entities:

        situacion = int(e.get("situacion", 1) or 1)
        dias_atraso = int(e.get("diasAtrasoPago", 0) or 0)
        amount = int(e.get("monto", 0) or 0) * 1000

        total_debt += amount

        if situacion > worst_situation:
            worst_situation = situacion

        if dias_atraso > max_days_late:
            max_days_late = dias_atraso

        if (
            e.get("refinanciaciones")
            or e.get("recategorizacionOblig")
            or e.get("situacionJuridica")
            or e.get("irrecDisposicionTecnica")
            or e.get("enRevision")
            or e.get("procesoJud")
        ):
            legal_flags = True

    historical_worst = 1
    late_days_list = []
    situation_variations = []

    for p in periods:

        for e in p.get("entidades", []):

            situacion = int(e.get("situacion", 1) or 1)
            dias_atraso = int(e.get("diasAtrasoPago", 0) or 0)

            if situacion > 0:
                situation_variations.append(situacion)

            if situacion > historical_worst:
                historical_worst = situacion

            late_days_list.append(dias_atraso)

    avg_days_late = 0

    if late_days_list:
        avg_days_late = sum(late_days_list) / len(late_days_list)

    stability_score = len(set(situation_variations)) if situation_variations else 1

    debt_trend = calculate_debt_trend(periods)

    return {
        "total_debt": total_debt,
        "entities": entity_count,
        "situation": worst_situation,
        "days_late": max_days_late,
        "legal_flags": legal_flags,
        "historical_worst": historical_worst,
        "avg_days_late": avg_days_late,
        "stability_score": stability_score,
        "debt_trend": debt_trend,
    }


def estimate_existing_installment(total_debt):

    return total_debt * 0.20


def calculate_score(data, salary):

    base_score = situation_to_score(data["situation"])

    existing_installment = estimate_existing_installment(data["total_debt"])

    if salary > 0:
        dti = existing_installment / salary
    else:
        dti = 1

    dti = min(dti, 3)

    penalty_debt = dti * 150
    penalty_entities = data["entities"] * 10
    penalty_late = data["days_late"] * 2
    penalty_history = data["historical_worst"] * 20
    penalty_behavior = data["avg_days_late"] * 1.5
    penalty_instability = data["stability_score"] * 10
    penalty_trend = trend_penalty(data["debt_trend"])

    score = (
        base_score
        - penalty_debt
        - penalty_entities
        - penalty_late
        - penalty_history
        - penalty_behavior
        - penalty_instability
        - penalty_trend
    )

    if data["legal_flags"]:
        score -= 200

    score = max(300, min(850, score))

    return round(score), existing_installment, dti


def determine_loan_term(score):

    if score >= 750:
        return 36
    elif score >= 650:
        return 24
    elif score >= 550:
        return 18
    else:
        return 12


def calculate_loan_from_installment(installment, months, annual_rate):

    if installment <= 0:
        return 0

    monthly_rate = (1 + annual_rate) ** (1 / 12) - 1

    if monthly_rate <= 0:
        return installment * months

    factor = ((1 + monthly_rate) ** months - 1) / (
        monthly_rate * (1 + monthly_rate) ** months
    )

    loan_amount = installment * factor

    return loan_amount


def calculate_loan_terms(salary, existing_installment, score, annual_rate):

    max_installment = salary * 0.30

    available_installment = max_installment - existing_installment

    if available_installment < 0:
        available_installment = 0

    term = determine_loan_term(score)

    loan_amount = calculate_loan_from_installment(
        available_installment,
        term,
        annual_rate,
    )

    return loan_amount, available_installment, term


def calculate_expected_loss(pd, loan):

    return pd * LGD * loan


def loan_decision(score, pd, dti):

    if dti > 0.40:
        return "RECHAZADO"

    if score < 500:
        return "RECHAZADO"

    if pd > 0.25:
        return "RECHAZADO"

    if score >= 700:
        return "APROBADO"

    return "REVISION"


def calculate_credit_profile(cuil, salary, tna):

    annual_rate = tna / 100

    bcra_data = get_bcra_data(cuil)

    analysis = analyze_bcra_data(bcra_data)

    score, existing_installment, dti = calculate_score(analysis, salary)

    pd = calculate_pd(score)

    loan_amount, monthly_installment, term = calculate_loan_terms(
        salary,
        existing_installment,
        score,
        annual_rate,
    )

    expected_loss = calculate_expected_loss(pd, loan_amount)

    decision = loan_decision(score, pd, dti)

    total_payment = monthly_installment * term
    interest_paid = total_payment - loan_amount

    return {
        "cuil": cuil,
        "ingreso_mensual": salary,
        "score_crediticio": score,
        "probabilidad_incumplimiento": pd,
        "decision": decision,
        "prestamo_maximo_recomendado": round(loan_amount),
        "cuota_mensual_estimada": round(monthly_installment),
        "plazo_prestamo_meses": term,
        "tna": tna,
        "total_a_pagar": round(total_payment),
        "intereses_totales": round(interest_paid),
        "perdida_esperada": round(expected_loss),
        "analisis_bcra": {
            "deuda_total": analysis["total_debt"],
            "cantidad_entidades": analysis["entities"],
            "peor_situacion_actual": analysis["situation"],
            "peor_situacion_historica": analysis["historical_worst"],
            "dias_atraso_actual": analysis["days_late"],
            "promedio_dias_atraso": round(analysis["avg_days_late"], 2),
            "estabilidad_crediticia": analysis["stability_score"],
            "tendencia_deuda": round(analysis["debt_trend"], 3),
            "alertas_legales": analysis["legal_flags"],
            "cuota_estimada_actual": round(existing_installment),
            "ratio_deuda_ingreso": round(dti, 3),
        },
    }
