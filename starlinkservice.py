import argparse as U,sys
from collections import namedtuple as D
from math import sqrt as N,acos,degrees as V,floor

#%% Name Space
l='#'
k=open
j=str
T='user'
S='sat'
R=''
Q=float
M='Invalid line! '
L='interferers'
K=range
H='sats'
G=True
F=len
E='users'
B=False
A=print

#%%
C=D('Vector3',['x','y','z'])
W=C(0,0,0)
X=32
Y=[str(A)for A in range(1,X+1)]
Z=4
a=[chr(ord('A') + A) for A in range(0,Z)]
b=10.0
c=20.0
O=45.0

#%%
def J(vertex,point_a,point_b):
    G=point_b
    F=point_a
    B=vertex
    D=C(F.x-B.x,F.y-B.y,F.z-B.z)
    E=C(G.x-B.x,G.y-B.y,G.z-B.z)
    H=N(D.x**2+D.y**2+D.z**2)
    I=N(E.x**2+E.y**2+E.z**2)
    J=C(D.x/H,D.y/H,D.z/H)
    K=C(E.x/I,E.y/I,E.z/I)
    L=J.x*K.x+J.y*K.y+J.z*K.z
    M=min(1.0,max(-1.0,L))
    if abs(M-L)>1e-06:
        print(f"dot_product: {L} bounded to {M}")
    return V(acos(M))

# Check self-interferes
def d(scenario,solution):
    O=solution
    L=scenario
    print('Checking no sat interferes with itself...')
    for M in solution:
        C=solution[M];
        D=list(C.keys());
        Q=L['sats'][M]
        for I in range(F(C)):
            for N in range(I+1,len(C)):
                R=C[D[I]][1]
                S=C[D[N]][1]
                if R!=S:
                    continue
                T=C[D[I]][0]
                U=C[D[N]][0]
                V=L['users'][T]
                W=L['users'][U]
                P=J(Q,V,W)
                if P < b:
                    print(f"\tSat {M} beams {D[I]} and {D[N]} interfere.")
                    print(f"\t\tBeam angle: {P} degrees.")
                    return False
    print('\tNo satellite self-interferes.')
    return True

# Check non starlink saterlite interfere
def e(scenario,solution):
    F=solution
    C=scenario
    print('Checking no sat interferes with a non-Starlink satellite...')
    for D in F:
        N=C[H][D]
        for I in F[D]:
            O=F[D][I][0]
            P=C[E][O]
            for K in C[L]:
                Q=C[L][K]
                M=J(P,N,Q)
                if M < c :
                    print(f"\tSat {D} beam {I} interferes with non-Starlink sat {K}.")
                    print(f"\t\tAngle of separation: {M} degrees.")
                    return False
    print('\tNo satellite interferes with a non-Starlink satellite!')
    return True

# Check if one user is covered mulitple times and the user coverage percent
def f(scenario,solution):
    C=solution;
    print('Checking user coverage...')
    D=[]
    for I in C:
        for K in C[I]:
            H=C[I][K][0]
            if H in D:
                print(f"\tUser {H} is covered multiple times by solution!")
                return False
            D.append(H)
    J=len(scenario[E])
    L=len(D)
    A(f"{L/J*100}% of {J} total users covered.")
    return True

# Check user and saterlite angle within 45 degrees. Could see saterlite
def g(scenario,solution):
    F=scenario;
    D=solution;
    print('Checking each user can see their assigned satellite...')
    for C in D:
        for L in D[C]:
            I=D[C][L][0];
            M=F[E][I];
            N=F[H][C];
            K=J(M,W,N)
            if K<=180.0-O:
                P=j(K-90);
                A(f"\tSat {C} outside of user {I}'s field of view.")
                A(f"\t\t{P} degrees elevation.")
                A(f"\t\t(Min: {90-O} degrees elevation.)")
                return False
    print("\tAll users' assigned satellites are visible.")
    return True

#%% Read File and check format

# Check input data format, called by h
def I(object_type,line,dest):
    E=line;
    D=E.split()
    if D[0]!=object_type or F(D)!=5:
        print(M+E);
        return B
    else:
        H=D[1]
        try:
            I=Q(D[2])
            J=Q(D[3])
            K=Q(D[4])
        except:
            print("Can't parse location! "+E)
            return False
        dest[H]=C(I,J,K)
        return True

# Read file and check if the format is correct
def h(filename,scenario):
    K='interferer'
    F=filename;
    D=scenario;
    print('Reading scenario file '+F);
    J=k(F).readlines();
    D[H]={};
    D[E]={};
    D[L]={}
    for C in J:
        if l in C:
            continue
        elif C.strip() == R:
            continue
        elif K in C:
            if not I(K,C,D[L]):
                return False
        elif S in C:
            if not I(S,C,D[H]):
                return False
        elif T in C:
            if not I(T,C,D[E]):
                return False
        else:
            print(M+C);
            return False
    return True

# Read input, check data and format
def P(filename,scenario,solution):
    O=scenario;
    K=filename;
    J=solution
    if K=='':
        print('Reading solution from stdin.')
        L=sys.stdin
    else:
        print(f"Reading solution file {K}.")
        L=open(K)
    U=L.readlines()
    for D in U:
        C=D.split()
        if '#' in D:
            continue
        elif len(C)==0:
            continue
        elif len(C)==8:
            if C[0]!=S or C[2]!='beam'or C[4]!=T or C[6]!='color':
                print(M+D)
                return False
            I=C[1]
            N=C[3]
            P=C[5]
            Q=C[7]
            if not I in O[H]:
                print('Referenced an invalid sat id! '+D)
                return False
            if not P in O[E]:
                print('Referenced an invalid user id! '+D)
                return False
            if not N in Y:
                print('Referenced an invalid beam id! '+D)
                return False
            if not Q in a:
                print('Referenced an invalid color! '+D)
                return B
            if not I in J:
                J[I]={}
            if N in J[I]:
                print('Beam is allocated multiple times! '+D) 
                return False
            J[I][N]=P,Q
        else:
            print(M+D)
            return False
    L.close()
    return True

#%% main function, read data, check criteria
def i():
    D=U.ArgumentParser(prog=f"python3.7 {sys.argv[0]}",description='Starlink beam-planning evaluation tool')
    D.add_argument('scenario',metavar='/path/to/scenario.txt',help='Test input scenario.')
    D.add_argument('solution',metavar='/path/to/solution.txt',nargs='?',help='Optional. If not provided, stdin will be read.')
    E=D.parse_args()
    B={}
    if not h(E.scenario,B):
        return -1
    C={}
    print(B)
    print(C)
    if E.solution is None:
        if not P(R,B,C):
            return -1
    elif not P(E.solution,B,C):
        return -1
    if not f(B,C):
        return -1
    if not g(B,C):
        return -1
    if not d(B,C):
        return -1
    if not e(B,C):
        print('Solution contained a beam that could interfere with a non-Starlink satellite.')
        return -1
    print('\nSolution passed all checks!\n');
    return 0

if __name__=='__main__':
    #exit(i())
    sys.exit(i())