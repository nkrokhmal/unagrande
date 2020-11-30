from utils_ak.interactive_imports import *
from app.schedule_maker.utils.block import validate_disjoint


def boiling_validator(parent, boiling):
    if not parent.children:
        return

    boilings = [node for node in parent.children if node.props['class'] == 'boiling']

    b2 = boiling
    b2.rel_props['props_mode'] = 'absolute'
    b2.upd_abs_props()

    # compare with previous boiling and with previous boiling on the same line
    for b1 in reversed(boilings[-4:]): # four checks is enough
        b1.rel_props['props_mode'] = 'absolute'
        b1.upd_abs_props()

        validate_disjoint(b1['pouring'][0]['termizator'], b2['pouring'][0]['termizator'])

        if b1['pouring'].props['pouring_line'] == b2['pouring'].props['pouring_line']:
            validate_disjoint(b1['pouring'], b2['pouring'])

        if b1.props['boiling_type'] == b2.props['boiling_type']:
            boiling_type = b1.props['boiling_type']
            if boiling_type == 'water':
                if b1.props['boiling_id'] == b2.props['boiling_id']:
                    # merging allowed
                    validate_disjoint(b1['melting_and_packing']['melting'][2]['melting_process'], b2['melting_and_packing']['melting'][2]['melting_process'])
                else:
                    validate_disjoint(b1['melting_and_packing']['melting'], b2['melting_and_packing']['melting'])
            else:
                if b1['melting_and_packing']['melting'].props['melting_line'] == b2['melting_and_packing']['melting'].props['melting_line']:
                    validate_disjoint(b1['melting_and_packing']['melting'], b2['melting_and_packing']['melting'])
                else:
                    validate_disjoint(b1['melting_and_packing']['melting'][1]['melting_process'],
                                      b2['melting_and_packing']['melting'][1]['melting_process'])

            validate_disjoint(b1['melting_and_packing']['packing'], b2['melting_and_packing']['packing'])

        b1.rel_props.pop('props_mode')
        b1.upd_abs_props()

    # no intersection with cleanings also
    cleanings = [node for node in parent.children if node.props['class'] == 'cleaning']
    if cleanings:
        c = cleanings[-1]

        c.rel_props['props_mode'] = 'absolute'
        c.upd_abs_props()

        validate_disjoint(c, b2['pouring'][0]['termizator'])

        c.rel_props.pop('props_mode')
        c.upd_abs_props()
    b2.rel_props.pop('props_mode')
    b2.upd_abs_props()

