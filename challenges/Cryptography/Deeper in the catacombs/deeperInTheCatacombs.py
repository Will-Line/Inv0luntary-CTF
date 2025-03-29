#Using modified code from Amaterazu7 on github

import socket
import random

IP = "127.0.0.1"
PORT = 5007

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_STREAM) # UDP
sock.bind((IP, PORT))


'''
Euclid's algorithm for determining the greatest common divisor
Use iteration to make it faster for larger integers
'''


def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a


'''
Euclid's extended algorithm for finding the multiplicative inverse of two numbers
'''


def multiplicative_inverse(e, phi):
    d = 0
    x1 = 0
    x2 = 1
    y1 = 1
    temp_phi = phi

    while e > 0:
        temp1 = temp_phi//e
        temp2 = temp_phi - temp1 * e
        temp_phi = e
        e = temp2

        x = x2 - temp1 * x1
        y = d - temp1 * y1

        x2 = x1
        x1 = x
        d = y1
        y1 = y

    if temp_phi == 1:
        return d + phi


'''
Tests to see if a number is prime.
'''


def is_prime(num):
    if num == 2:
        return True
    if num < 2 or num % 2 == 0:
        return False
    for n in range(3, int(num**0.5)+2, 2):
        if num % n == 0:
            return False
    return True


def generate_key_pair(p, q):
    # n = pq
    n = p * q

    # Phi is the totient of n
    phi = (p-1) * (q-1)

    # Choose an integer e such that e and phi(n) are coprime
    e = 65537

    # Use Euclid's Algorithm to verify that e and phi(n) are coprime

    # Use Extended Euclid's Algorithm to generate the private key
    d = multiplicative_inverse(e, phi)

    # Return public and private key_pair
    # Public key is (e, n) and private key is (d, n)
    return ((e, n), (d, n))


def encrypt(pk, plaintext):
    # Unpack the key into it's components
    key, n = pk

    cipher = int("".join(map(str, [(ord(char)) for char in plaintext])))
    cipher=pow(cipher,key,n)
    # Return the array of bytes
    return cipher

def decrypt(pk, ciphertext):
    # Unpack the key into its components
    key, n = pk
    # Generate the plaintext based on the ciphertext and key using a^b mod m
    aux = str(pow(ciphertext, key, n))
    # Return the array of bytes as a string
    plain=""
    #for i in range(0,len(aux),3):
     #   letter=int(aux[i]+aux[i+1]+aux[i+2])
      #  plain+=chr(letter)
    return aux

# Pre generated primes
first_primes_list = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
                     31, 37, 41, 43, 47, 53, 59, 61, 67,
                     71, 73, 79, 83, 89, 97, 101, 103,
                     107, 109, 113, 127, 131, 137, 139,
                     149, 151, 157, 163, 167, 173, 179,
                     181, 191, 193, 197, 199, 211, 223,
                     227, 229, 233, 239, 241, 251, 257,
                     263, 269, 271, 277, 281, 283, 293,
                     307, 311, 313, 317, 331, 337, 347, 349]
 
 
def nBitRandom(n):
    return random.randrange(2**(n-1)+1, 2**n - 1)
 
 
def getLowLevelPrime(n):
    '''Generate a prime candidate divisible 
    by first primes'''
    while True:
        # Obtain a random number
        pc = nBitRandom(n)
 
        # Test divisibility by pre-generated
        # primes
        for divisor in first_primes_list:
            if pc % divisor == 0 and divisor**2 <= pc:
                break
        else:
            return pc
 

def isMillerRabinPassed(mrc):
    '''Run 20 iterations of Rabin Miller Primality test'''
    maxDivisionsByTwo = 0
    ec = mrc-1
    while ec % 2 == 0:
        ec >>= 1
        maxDivisionsByTwo += 1
    assert(2**maxDivisionsByTwo * ec == mrc-1)
 
    def trialComposite(round_tester):
        if pow(round_tester, ec, mrc) == 1:
            return False
        for i in range(maxDivisionsByTwo):
            if pow(round_tester, 2**i * ec, mrc) == mrc-1:
                return False
        return True
 
    # Set number of trials here
    numberOfRabinTrials = 20
    for i in range(numberOfRabinTrials):
        round_tester = random.randrange(2, mrc)
        if trialComposite(round_tester):
            return False
    return True


if __name__ == '__main__':
    sock.listen(0)
    client_socket, client_address = sock.accept()

    p=0
    q=0

    coPrime=False

    while coPrime==False:
        while True:
            n = 1024
            prime_candidate = getLowLevelPrime(n)
            if not isMillerRabinPassed(prime_candidate):
                continue
            else:
                #print(n, "bit prime is: \n", prime_candidate)
                p=prime_candidate
                break

        while True:
            n = 1024
            prime_candidate = getLowLevelPrime(n)
            if not isMillerRabinPassed(prime_candidate):
                continue
            else:
                #print(n, "bit prime is: \n", prime_candidate)
                q=prime_candidate
                break

        if gcd((p-1)*(q-1),65537)==1:
            coPrime=True

        
                

    client_socket.send(" - Generating your public / private key-pairs now . . .\n".encode("utf-8"))

    public, private = generate_key_pair(p, q)

    client_socket.send((f" - Your public key is ({public[0]},{public[1]})\n").encode("utf-8"))
    if private[0]!=None:
        flag=encrypt(public,"!FLAG!{RSA_n0_problem}!FLAG! ")
        client_socket.send((f"\n Here's some cryptography I did earlier: {flag}\n").encode("utf-8"))
        #message = input(" - Enter a message to encrypt with your public key: ")
        client_socket.send(" - Enter a message to encrypt with your public key: ".encode("utf-8"))
        message=client_socket.recv(1024).decode("utf-8")
        encrypted_msg = encrypt(public, message)

        client_socket.send((f" - Your encrypted message is: {encrypted_msg}\n").encode("utf-8"))
        
        #cipher_text=int(input("- Enter some cipher text to decrypt with the private key: "))
        client_socket.send("- Enter some cipher text to decrypt with the private key: ".encode("utf-8"))
        cipher_text=int(client_socket.recv(1024).decode("utf-8"))

        if cipher_text==flag:
            client_socket.send("You're not allowed to do that\n".encode("utf-8"))
        else:
            client_socket.send((f"- Your decrypted cipher text is: {decrypt(private,cipher_text)}\n").encode("utf-8"))

    client_socket.send("============================================ END ==========================================================".encode("utf-8"))

    client_socket.close()
