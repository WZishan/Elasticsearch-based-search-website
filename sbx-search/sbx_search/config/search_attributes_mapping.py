attribute_mapping = {
    'investments': [
        'standardized_investment_name',
        'oe_investment_name',
        'direct_issuer',
        'ultimate_issuer',
        'cons_unit_name',
        'local_portfolio_l5',
        'country_of_risk',
        'cart_l1',
        'cart_l2',
        'cart_l3',
        'cart_l4'
    ],
    'cons_units': [
        'cons_unit_code',
        'cons_unit_name'
    ],
    'mandates': [
        'local_portfolio_l5'
    ],
    'ultimate_issuers': [
        'ultimate_issuer'
    ],
    'cart': [
        'cart'
    ],
    'country_of_risk': [
        'country_of_risk'
    ]
}


def get_default_attributes(index_name: str):
    return attribute_mapping[index_name.split('-')[-1]]
