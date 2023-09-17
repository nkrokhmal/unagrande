STYLE = {
    "boiling_preparation": {"text": "Подготовка", "color": "white"},
    "pouring": {"text": "Набор сыворотки 6500 кг", "color": "#00B050"},
    "heating": {"text": "Нагрев до 90 градусов", "color": "#E26B0A"},
    "lactic_acid": {"text": "Молочная кислота/выдерживание", "color": "#00B0F0"},
    "draw_whey": {"text": "Слив сыворотки", "color": "#FFC000"},
    "draw_ricotta": {"text": "Слив рикотты 500 кг п/ф", "color": "#948A54"},
    "draw_ricotta_break": {"text": "", "color": "white"},
    "salting": {"text": "Посолка/анализ", "color": "#D9D9D9"},
    "pumping": {"text": "Перекачивание", "color": "#00B050"},
    "cleaning": {
        "text": lambda b: {
            "floculator": f"Мойка флокулятора №{b.props['floculator_num']}",
            "drenator": "Мойка дренатора",
            "lishat_richi": "Мойка 1-го и 2-го бакол лишатричи + Бертоли",
            "buffer_tank": "Мойка буферного танка и Фасовочника Ильпра",
        }[b.props["cleaning_object"]],
        "color": "#92D050",
    },
    "shift": {
        "text": lambda b: f"Смена {b.props['shift_num'] + 1} {b.props['team']}",
        "color": lambda b: ["yellow", "#95B3D7"][b.props["shift_num"]],
    },
    "preparation": {
        "text": "подготовка цеха к работе, проверка оборудования стерилизация оборудования  , вызов микробиолога, отбор анализов, разгон сепаратора",
        "color": "white",
    },
    "template": {"color": "white"},
}
