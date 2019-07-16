import sympy as sp
from .expansions import M, M_shift, L, L_shift, phi_deriv
from sympy.polys.orderings import monomial_key
from .utils import itermonomials, generate_mappings, Nterms
from sympy.polys.monomials import itermonomials as sp_itermonomials

def itermonomials(symbols, max_degree, min_degree=0):
    monoms = list(sp_itermonomials(symbols, max_degree))
    new_monoms = []
    for monom in monoms:
        monom_dict = monom.as_powers_dict()
        order = 0
        for symbol in symbols:
            order += monom_dict[symbol]
            if order >= min_degree:
                new_monoms.append(monom)
    return set(new_monoms)


def generate_mappings(order, symbols, key='grevlex', source_order=0):
    """
    generate_mappings(order, symbols, key='grevlex'):

    Generates a set of mappings between three-tuples of
    indices denoting monomials and and array indices.
    Returns both the forward and backward maps.

    Inputs:
    order: int
        Maximum monomial order

    symbols: list
        List of sympy.Symbol type objects

    source_order: int
        Integer describing order of o

    Returns:
    dict:
        Forward mapping from n-tuple to array index.

    dict:
        Reversed version; mapping from array index to
        tuple mapping.

    Example:
    >>> x, y, z = sp.symbols('x y z')
    >>> map, rmap = generate_mappings(1, [x, y, z])
    >>> print(map):
    {(0, 0, 0): 0, (1, 0, 0): 1, (0, 1, 0): 2, (0, 0, 1): 3}
    >>> print(rmap):
    {0: (0, 0, 0), 1: (1, 0, 0), 2: (0, 1, 0), 3: (0, 0, 1)}
    """
    if order < source_order:
        raise ValueError(
            "source_order must be <= order for meaningful calculations to occur"
        )

    x, y, z = symbols
    rsymbols = [z, y, x]

    monoms = itermonomials(symbols, order, source_order)
    if key:
        monom_key = monomial_key(key, rsymbols)
        monoms = sorted(monoms, key=monom_key)

    index_dict = {}
    rindex_dict = {}
    for i, monom in enumerate(monoms):
        d = monom.as_powers_dict()
        n = d[x], d[y], d[z]
        index_dict[n] = i
        rindex_dict[i] = n
    return index_dict, rindex_dict


def generate_M_operators(order, symbols, M_dict):
    """
    generate_M_operators(order, symbols, index_dict):

    Generates multipole operators up to order.

    Input:
    order, int:
        Maximum order of multipole expansion

    symbols, list:
        List of sympy symbol type objects which
        define coordinate labels.

    index_dict:
        Forward mapping dictionary between
        monomials of symbols and array indices,
        generated by generate_mappings or otherwise.

    Output:
    list:
        List of symbolic multipole moments up to order.

    Example:
    >>> order = 2
    >>> x, y, z = sp.symbols('x y z')
    >>> map, _ = generate_mappings(order, [x, y, z])
    >>> generate_M_operators(order, (x, y, z), map)
    [q, -q*x, -q*y, -q*z, q*x**2/2, q*x*y, q*x*z, q*y**2/2, q*y*z, q*z**2/2]
    """
    x, y, z = symbols
    M_operators = []
    for n in M_dict.keys():
        M_operators.append(M(n, symbols))
    return M_operators


def generate_M_shift_operators(order, symbols, M_dict, source_order=0):
    """
    generate_M_shift_operators(order, symbols, index_dict):

    Generates multipole shifting operators up to order.

    Input:
    order, int:
        Maximum order of multipole expansion

    symbols, list:
        List of sympy symbol type objects which define coordinate labels.

    index_dict:
        Forward mapping dictionary between
        monomials of symbols and array indices, generated by generate_mappings
         or otherwise.

    Output:
    list:
        List of symbolic multipole shifting operators up to order.

    Example:
    >>> order = 1
    >>> x, y, z = sp.symbols('x y z')
    >>> map, _ = generate_mappings(order, [x, y, z])
    >>> generate_M_shift_operators(order, (x, y, z), map)
    [M[0, 0], x*M[0, 0] + M[1, 0], y*M[0, 0] + M[2, 0], z*M[0, 0] + M[3, 0]]
    """
    x, y, z = symbols
    M_operators = []
    for n in M_dict.keys():
        M_operators.append(M_shift(n, order, symbols, M_dict,
                                   source_order=source_order))
    return M_operators


def generate_L_operators(order, symbols, M_dict, L_dict, source_order=0):
    """
    generate_L_operators(order, symbols, index_dict):

    Generates local expansion operators up to given order.

    Input:
    order, int:
        Maximum order of multipole expansion

    symbols, list:
        List of sympy symbol type objects which define coordinate labels.

    index_dict:
        Forward mapping dictionary between
        monomials of symbols and array indices, generated by generate_mappings
        or otherwise.

    inline_derivs: bool
        Calculate derivatives inline rather than precalculating these.

    Output:
    list:
        List of symbolic local expansion operators up to order.

    Example:
    >>> order = 1
    >>> x, y, z = sp.symbols('x y z')
    >>> map, _ = generate_mappings(order, (x, y, z))
    >>> generate_L_operators(order, (x, y, z), map)
    [M[0, 0]/R - 1.0*x*M[1, 0]/R**3 - 1.0*y*M[2, 0]/R**3 - 1.0*z*M[3, 0]/R**3,
    -1.0*x*M[0, 0]/R**3, -1.0*y*M[0, 0]/R**3, -1.0*z*M[0, 0]/R**3]
    """
    x, y, z = symbols
    L_operators = []
    for n in L_dict.keys():
        L_operators.append(L(n, order, symbols, M_dict, source_order=source_order))
    return L_operators


def generate_L_shift_operators(order, symbols, L_dict, source_order=0):
    """
    generate_L_shift_operators(order, symbols, index_dict):

    Generates multiple operators up to order.

    Input:
    order, int:
        Maximum order of multipole expansion

    symbols, list:
        List of sympy symbol type objects which
        define coordinate labels.

    index_dict:
        Forward mapping dictionary between
        monomials of symbols and array indices,
        generated by generate_mappings or otherwise.

    Output:
    list:
        List of symbolic local expansion shifting operators up to order.

    Example:
    >>> order = 1
    >>> x, y, z = sp.symbols('x y z')
    >>> map, _ = generate_mappings(order, (x, y, z))
    >>> generate_L_shift_operators(order, (x, y, z), map)
    [x*L[1, 0] + y*L[2, 0] + z*L[3, 0] + L[0, 0], L[1, 0], L[2, 0], L[3, 0]]
    """
    x, y, z = symbols
    L_shift_operators = []
    for n in L_dict.keys():
        L_shift_operators.append(L_shift(n, order, symbols, L_dict, source_order=source_order))
    return L_shift_operators


def generate_M2P_operators(order, symbols, M_dict,
                           potential=True, field=True, source_order=0):
    """
    generate_M2L_operators(order, symbols, index_dict)

    Generates potential and field calculation operators for the
    Barnes-Hut method up to order.
    """
    x, y, z = symbols
    R = (x**2 + y**2 + z**2)**0.5

    terms = []

    V = L((0, 0, 0), order, symbols, M_dict, source_order=source_order).subs('R', R)
    if potential:
        terms.append(V)

    if field:
        Fx = -sp.diff(V, x)
        Fy = -sp.diff(V, y)
        Fz = -sp.diff(V, z)
        terms.append(Fx)
        terms.append(Fy)
        terms.append(Fz)

    return terms

def generate_L2P_operators(order, symbols, L_dict, potential=True, field=True):
    """
    generate_L2P_operators(order, symbols, index_dict):

    Generates potential and field calculation operators for the Fast
    Multipole Method up to order.

    Input:
    order, int:
        Maximum order of multipole expansion

    symbols, list:
        List of sympy symbol type objects which define coordinate labels.

    index_dict:
        Forward mapping dictionary between monomials of symbols and array
        indices, generated by generate_mappings or otherwise.

    Output:
    list:
        List of symbolic field calculation operators from local expansions up to
        order.

    Example:
    >>> order = 1
    >>> x, y, z = sp.symbols('x y z')
    >>> map, _ = generate_mappings(order, (x, y, z))
    >>> generate_L2P_operators(order, (x, y, z), map)
    [x*L[1, 0] + y*L[2, 0] + z*L[3, 0] + L[0, 0], -L[1, 0], -L[2, 0], -L[3, 0]]
    """
    x, y, z = symbols

    terms = []

    if potential:
        V = phi_deriv(order, symbols, L_dict, deriv=(0, 0, 0))
        terms.append(V)

    if field:
        Fx = -phi_deriv(order, symbols, L_dict, deriv=(1, 0, 0))
        Fy = -phi_deriv(order, symbols, L_dict, deriv=(0, 1, 0))
        Fz = -phi_deriv(order, symbols, L_dict, deriv=(0, 0, 1))
        terms.append(Fx)
        terms.append(Fy)
        terms.append(Fz)
    return terms

def generate_P2P_operators(symbols, M_dict, potential=True, field=True, source_order=0):
    order = source_order
    M_dict, _ = generate_mappings(source_order, symbols, 'grevlex',
                                  source_order=source_order)
    x, y, z = sp.symbols('x y z')
    R = (x**2 + y**2 + z**2) ** 0.5

    S_map, _ = generate_mappings(source_order, [x, y, z], key='grevlex',
                                 source_order=source_order)
    print('S_map = {}'.format(S_map))

    M = sp.MatrixSymbol('M', Nterms(order), 1)
    S = sp.MatrixSymbol('S', Nterms(order), 1)

    subsdict = {M[i]: 0 for i in range(Nterms(order))}

    for key in S_map.keys():
        subsdict[M[M_dict[key]]] = S[M_dict[key]]

    V = L((0, 0, 0), order, symbols, M_dict, source_order=source_order).subs('R', R).subs(subsdict)

    terms = []
    # Note: R must be substituted late for correct derivatives!
    if potential:
        terms.append(V.subs(R, 'R'))

    if field:
        Fx = -sp.diff(V, x).subs(R, 'R')
        Fy = -sp.diff(V, y).subs(R, 'R')
        Fz = -sp.diff(V, z).subs(R, 'R')
        terms.append(Fx)
        terms.append(Fy)
        terms.append(Fz)
    return terms
