# This is a hokey approximation of a perceptual difference between images.

def difference(a, b):
    L = 25
    a.thumbnail((L,L))
    b.thumbnail((L,L))
    A = a.tostring()
    B = b.tostring()
    err = 0.0
    norm = 0.0
    for i in range(L-1):
        for j in range(L-1):
            for color in [0,1,2]:
                dxA =    float(ord(A[4*i + 4*j*L + color])) - float(ord(A[4*(i+1) + 4*j*L + color]))
                dyA =    float(ord(A[4*i + 4*j*L + color])) - float(ord(A[4*i + 4*(j+1)*L + color]))
                meanxA = float(ord(A[4*i + 4*j*L + color])) + float(ord(A[4*(i+1) + 4*j*L + color]))
                meanyA = float(ord(A[4*i + 4*j*L + color])) + float(ord(A[4*i + 4*(j+1)*L + color]))

                dxB = float(ord(B[4*i + 4*j*L + color])) - float(ord(B[4*(i+1) + 4*j*L + color]))
                dyB = float(ord(B[4*i + 4*j*L + color])) - float(ord(B[4*i + 4*(j+1)*L + color]))
                meanxB = float(ord(B[4*i + 4*j*L + color])) + float(ord(B[4*(i+1) + 4*j*L + color]))
                meanyB = float(ord(B[4*i + 4*j*L + color])) + float(ord(B[4*i + 4*(j+1)*L + color]))

                err += (dxA-dxB)**2 + (dyA-dyB)**2 + 0.3*((meanyA-meanyB)**2 + (meanxA - meanxB)**2)#square rooting could help????
                norm += 256.0*2
    return err/norm
