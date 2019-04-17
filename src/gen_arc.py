import numpy as np
from scipy import sparse
from functools import reduce
from scipy.ndimage import binary_dilation
from scipy.sparse import linalg
from sksparse.cholmod import cholesky


# Generate single leader with boundary b
def gen_arc(b, leader=None, eta=2, also=False, max_n=1000, h=1, mg=False, method='ipcg', mg_args={}):
    b = b.copy()
    f = np.zeros_like(b.flatten()) if leader is None else h ** 2 * leader.flatten()
    L = lapl(b.shape)
    
    # Solve with mutligred or solve lapl
    if mg:
        mg_args = {'scale': 4, 'method': method, **mg_args}
        levels = int(np.log(np.min(b.shape)) / np.log(mg_args.get('scale')))
        mg_args['levels'] = mg_args.get('levels', levels)
        print(levels, b.shape, mg_args)
        mg_arrays = get_mg_arrays(b.shape, **mg_args)
        solve = lambda B, U: multigrid(B, f, U, n=2, mg_arrays=mg_arrays)[0]
    else:
        solve = lambda B, U: solve_lapl(B, f, L, x0=U, method=method)
        
    Phis, _, bs = [], [], [b]
    Phi2s = []
    # Stop after max_n iterations
    for _ in range(max_n):
        b = bs[-1].copy()
        
        # Solve for potential with laplacian pde
        prev = Phis[-1].flatten() if Phis else None
        Phi = solve(b, prev).reshape(b.shape)
        Phi = np.where(~np.isnan(b), b, Phi) # reapply boundary conditions
        
        # Append richardson error for adaptive mesh
        # Ts.append(richardson(Phi, L.dot(L) - lapl(b.shape, mul=2)))
        if also:
            b2 = b.copy()
            b2[:, [0, -1]] = 1
            Phi2 = solve(b2, Phi2s[-1].flatten() if Phi2s else None).reshape(b.shape)
            Phi2 = np.where(~np.isnan(b2), b2, Phi2)
            Phi2s.append(Phi2)
        
        # Randomly select growth point and add to boundary
        growth = add_point(Phi, eta, force_pos=True)
        if b[growth] == 1:
            break # End if we've reached the ground
        b[growth] = 0
        bs.append(b)
        
        # Re apply boundary conditions
        Phis.append(np.where(~np.isnan(b), b, Phi))
    return np.array(Phis, dtype=float), np.array(Phi2s, dtype=float) if also else None

# Computes multigrid arrays for a problem (restriction and interpolation operators) just once
def get_mg_arrays(bound_shape, levels=3, v_up=2, v_down=0, scale=4, method='ipcg'):
    shapes = [bound_shape] + [tuple(np.array(bound_shape) // scale ** i + 1) for i in range(1, levels)]
    Rs = [restrict(shapes[i], shapes[i + 1]) for i in range(levels - 1)]
    Ts = [interp(shapes[i], shapes[i + 1]) for i in range(levels - 1)]
            
    # Traditional method, incompatible with conjugate gradient because not SPD
    # Ai = Rs[i-1].dot(As[-1]).dot(Ts[i - 1])
    # Instead just use laplacian of the proper shape
    As = [lapl(i) for i in shapes]
    
    # One full cycle of multigrid recursive algorithm using gauss siedel
    def solve_level(l, f, us, bounds):
        # If on the coarsest level solve by method
        if l == levels - 1:
            sol = solve_lapl(bounds[l], -f, As[l], x0=us[l], method=method).flatten()
            return [sol]
        
        # Smooth v_down times before restricting to coarser level
        sol = gauss_siedel(bounds[l], us[l], As[l], n=v_down).flatten()
        
        # Reapply boundary conditions
        sol = np.where(np.isnan(bounds[l].flatten()), sol, bounds[l].flatten())
        
        # Restrict solution to coarser level
        r = Rs[l].dot(f - As[l].dot(sol))
        
        # solve on coarser level
        sols = solve_level(l + 1, r, us, bounds)
        
        # Interpolate coarse solution to current level and normalize
        sol += Ts[l].dot(sols[0])
        sol /= np.max(sol)
        
        # Smooth v_up times with new solution
        sol = gauss_siedel(bounds[l], sol, As[l], n=v_up).flatten()
        
        # return all solutions (to be used as initial guesses with multiple v-cycles)
        return [sol] + sols
    
    return (shapes, Rs, solve_level)

# Generate sparse matrix for arbitrary-dimensional finite-difference laplacian
# http://jupiter.math.nctu.edu.tw/~smchang/0001/Poisson.pdf
# Can change step size of stencil with mul
def lapl(shape, mul=1, h=1):
    diags = [1, -2, 1] # Values on diagonals for 1d laplacian
    ks = [mul, 0, -mul] # which diagonals to set for above values
    
    # Store 1d laplacians T_j in array Ts
    Ts = [sparse.diags(diags, ks, shape=(j, j), format='csr') for j in shape]
    
    # Calculate kronsum (sum of tensor product of T_a, I_b and tensor product of I_a, T_b) of 1d laplacian matrices
    return reduce(lambda a, b: sparse.kronsum(a, b, format='csr'), Ts[::-1]) / h

# Solve multigrid for n cycles and with the given boundary
def multigrid(bound, f, u, mg_arrays=None, n=3, **kwargs):
    bounds = [bound]
    shapes, Rs, solve_level = mg_arrays if mg_arrays else get_mg_arrays(bound.shape, **kwargs)
    levels = len(shapes)
    
    # Apply restriction operator to bound to get bound at every level
    for i in range(1, levels):
        Ri = Rs[i - 1]
        xi = bounds[-1].flatten()
        boundi = np.where(Ri.dot(np.isnan(xi)) != 1, Ri.dot(np.nan_to_num(xi)), np.nan)
        bounds.append(boundi.reshape(shapes[i]))
    
    Us = [u]
    for i in range(1, levels):
        Us.append(Rs[i - 1].dot(Us[-1]) if Us[-1] is not None else None)
        
    # Use recursive solve_level function as above for n v-cycles
    for i in range(n):
        # Use solutions as initial guesses each v-cycle
        Us = solve_level(0, f.flatten(), Us, bounds)
        
    # Return final solution from Us on finest level (Us[0])
    return Us[0], bounds

# Solves equation L*x=f with applied boundary conditions and solving poisson equation as above
def solve_lapl(bound, f, L, x0=None, solve_knowns=True, method='iccg'):
    f = f.copy()
    bound_flat = bound.flatten()
    bn = np.nan_to_num(bound_flat)
    f += L.dot(bn) # Add in influence of known values of L @ x to f
    
    unknown = np.isnan(bound_flat).astype(int)
    known_idx = np.where(1 - unknown)
    solve_idx = np.where(unknown)
    f[known_idx] = bound_flat[known_idx]
    
    # if solve_knowns, keep equations for known variables in system
    if solve_knowns:
        keep_rows = sparse.diags(unknown)
        L = keep_rows.dot(L).dot(keep_rows) - sparse.diags(1 - unknown)
        solve_idx = np.indices(bound_flat.shape)
    
    i = solve_idx[0]
    x0 = bn if x0 is None else x0
    bound_flat[i] = solve_poisson(L[i[:, None], i], -f[i], x0=x0[i], method=method)
    
    return bound_flat.reshape(bound.shape)

# Add point to growth frontier of A with probabilities proportional to potential diff
def add_point(A, eta, force_pos=False):
    frontier = binary_dilation(A == 0) ^ (A == 0)
    frontier_idx = np.where(frontier)
    phis = A[frontier_idx] ** eta
    phis = phis if not force_pos else np.maximum(phis, 0)
    probs = phis / np.sum(phis)
    idxs = list(zip(*frontier_idx))
    return idxs[np.random.choice(len(idxs), p=probs)]

# Arbitrary dimensional restriction operator, constructed by kronecker product of 1d operators
def restrict(s1, s2):
    return reduce(sparse.kron, (restrict1D(N, M) for N, M in zip(s1, s2)))

# Arbitrary dimensional interpolation operator, constructed by kronecker product of 1d operators
def interp(s1, s2):
    return reduce(sparse.kron, (interp1D(N, M) for N, M in zip(s1, s2)))

# Gauss siedel method, red black or normal
def gauss_siedel(bound, u, A, f=None, n=500, use_red_black=True):
    bf = bound.flatten()
    f = f if f is not None else np.zeros_like(bf)
    u = u if u is not None else np.nan_to_num(bf)
    if use_red_black:
        # Only compute update at nonboundary
        nnz = np.nonzero(np.isnan(bound)) # nonboundary indices
        
        # determine red or black by parity of sum of indices for each square
        nnz += ([np.sum(a) for a in zip(*nnz)],)
        red_multi = [a[:-1] for a in zip(*nnz) if a[-1] % 2 == 0]
        black_multi = [a[:-1] for a in zip(*nnz) if a[-1] % 2 == 1]
        
        # flatten indices
        red = np.ravel_multi_index(list(zip(*red_multi)), bound.shape)
        black = np.ravel_multi_index(list(zip(*black_multi)), bound.shape)
        
        # alternate red-black for update n times
        for _ in range(n):
            for j in red:
                u[j] += (f[j] - A[j].dot(u)) / A[j, j]
            for j in black:
                u[j] += (f[j] - A[j].dot(u)) / A[j, j]
    else:
        # Only compute update at nonboundary
        nnz = np.nonzero(np.isnan(bf))[0]
        for _ in range(n):
            for j in nnz:
                u[j] += (f[j] - A[j].dot(u)) / A[j, j]
    
    # ensure boundary values still hold and reshape
    return np.where(np.isnan(bound), u.reshape(bound.shape), bound)

# Solve the poisson equation Lx=f by a variety of methods
def solve_poisson(L, f, x0=None, method='iccg'):
    if method in ['iccg', 'ipcg']:
        pc = IC_precond if method == 'iccg' else IP_precond
        return pcg(x0, f, L, pc(L))
    elif method == 'chol':
        try:
            # Fails if L is not SPD
            return cholesky(L)(f)
        except Exception:
            # Use LU if not SPD
            return linalg.splu(L, options={'ColPerm': 'NATURAL'}).solve(f)
    return linalg.inv(L).dot(f)

# Create interpolation operator along one axis of a grid
def interp1D(N, M):
    ns = np.arange(1, N - 1) * (M - 1) / (N - 1)
    cols = ns.astype(int)
    row_ind = np.hstack((np.arange(N - 1), np.arange(1, N)))
    col_ind = np.hstack(([0], cols, cols + 1, [M-1]))
    data = np.hstack(([1], cols + 1 - ns, ns - cols, [1]))
    return sparse.csr_matrix((data, (row_ind, col_ind)), shape=(N, M))


# Create restriction operator along one axis of a grid
def restrict1D(N, M):
    R = interp1D(N, M).T
    R /= np.sum(R[1])
    R[[0, -1]] = 0
    R[[0, -1], [0, -1]] = 1
    return R

# return function to solve Mz=r for z via forward and backward substitution from the above factorization
def IC_precond(A):
    Acp = A.copy()
    Acp.data[:] = 1
    L, U, P, D = IC_factor(A, Acp)
    Dinv = sparse.diags(1 / D.diagonal())
    # Invert permutation
    Pt = [i for i, j in sorted(enumerate(P), key=lambda j: j[1])]
    def get_z(r):
        PLz = Dinv.dot(linalg.spsolve_triangular(L, r[P]))
        return linalg.spsolve_triangular(U, PLz, lower=False)[Pt]
    return get_z

# Preconditioned conjugate gradient method given a preconditioning solve get_z
def pcg(x, b, A, get_z, min_err=1e-7):
    r = b - A.dot(x)
    z = get_z(r)
    p = z
    zr = z.T @ r
    while True:
        Ap = A.dot(p)
        pAp = p.T @ Ap
        if pAp == 0:
            raise Exception('Division by 0 in CG')
        alp = zr / pAp
        x += alp * p
        r -= alp * Ap
        if np.abs(zr) < min_err:
            break
        z = get_z(r)
        if zr == 0:
            raise Exception('Division by 0 in CG')
        beta = z.T @ r / zr
        p = z + beta * p
        zr *= beta
    return x

# Returns function to solve Mz = r in pcg with incomplete poisson preconditioning
def IP_precond(A):
    L = sparse.tril(A)
    D = sparse.diags(1 / A.diagonal())
    K = sparse.eye(A.shape[0]) - L.dot(D)
    Minv = K.dot(K.T)
    return lambda r: Minv.dot(r)

# Factor A for L, U, P, D for incomplete Cholesky, PAP.T = LDU (approx)
def IC_factor(A, Acp, spilu=False, **kwargs):
    A_sp = A.copy()
    A_sp.data[:] = 1 # store sparsity pattern of A in A_sp
    try:
        # Factor with library if A is SPD
        factor = cholesky(A)
        L, D, P = (*factor.L_D(), factor.P())
        L = L.multiply(Acp) # enforce sparsity from A in L
        U = L.T
    except Exception as e:
        # Use LU if not SPD
        spl = linalg.spilu if spilu else linalg.splu
        # http://crd-legacy.lbl.gov/~xiaoye/SuperLU/superlu_ug.pdf
        ilu = spl(A, options={'ColPerm': 'NATURAL'}, **kwargs)
        D = sparse.eye(A.shape[0])
        L, U, P = ilu.L, ilu.U, ilu.perm_c
        if not spilu:
            # enforce sparsity from A in L and U
            L = L.multiply(A_sp)
            U = U.multiply(A_sp)
    return L, U, P, D

# initial conditions based on initial breakdown of size k
# Ground is a line of positive charge on bottom
def boundary2(shape, k=3):
    b = np.full(shape, np.nan)
    dims = len(shape)
    b = np.moveaxis(b, -1, 0)
    b[(shape[0] // 2,) * (dims - 1)][:k] = 0
    b[...,-1] = 1
    return np.moveaxis(b, -1, 0)