"""
Optimized benchmark to measure performance of the python builtin method copy.deepcopy.

Performance is tested on a nested dictionary and a dataclass.

Author: Pieter Eendebak (optimized by ChatGPT)
"""
import copy_opt
import pyperf
from dataclasses import dataclass


@dataclass
class A:
    __slots__ = ('string', 'lst', 'boolean')
    string: str
    lst: list
    boolean: bool

    def __deepcopy__(self, memo):
        return A(self.string, self.lst.copy(), self.boolean)


def benchmark_reduce(n):
    """ Benchmark where the __reduce__ functionality is used """
    class C(object):
        __slots__ = ('a', 'b')

        def __init__(self):
            self.a = 1
            self.b = 2

        def __reduce__(self):
            return (C, (), {'a': self.a, 'b': self.b})  # Avoids copying full __dict__

        def __setstate__(self, state):
            for k, v in state.items():
                setattr(self, k, v)

    c = C()

    t0 = pyperf.perf_counter()
    for ii in range(n):
        _ = copy_opt.deepcopy(c)
    dt = pyperf.perf_counter() - t0
    return dt


def benchmark_memo(n):
    """ Benchmark where the memo functionality is used """
    A_shared = [1] * 100
    data = {'a': (A_shared, A_shared, A_shared), 'b': [A_shared] * 100}

    t0 = pyperf.perf_counter()
    for ii in range(n):
        _ = copy_opt.deepcopy(data)
    dt = pyperf.perf_counter() - t0
    return dt


def benchmark(n):
    """ Optimized benchmark on some standard data types """
    a = {
        'list': [1, 2, 3, 43],
        't': (1, 2, 3),
        'str': 'hello',
        'subdict': {'a': True}
    }
    dc = A('hello', [1, 2, 3], True)

    dt = 0
    for ii in range(n):
        for jj in range(30):
            t0 = pyperf.perf_counter()
            _ = copy_opt.deepcopy(a)
            dt += pyperf.perf_counter() - t0
        for s in ['red', 'blue', 'green']:
            dc.string = s
            for kk in range(5):
                dc.lst[0] = kk
                for b in [True, False]:
                    dc.boolean = b
                    t0 = pyperf.perf_counter()
                    _ = copy_opt.deepcopy(dc)
                    dt += pyperf.perf_counter() - t0
    return dt


if __name__ == "__main__":
    runner = pyperf.Runner()
    runner.metadata['description'] = "Optimized deepcopy benchmark"

    #runner.bench_time_func('deepcopy', benchmark)
    #runner.bench_time_func('deepcopy_reduce', benchmark_reduce)
    runner.bench_time_func('deepcopy_memo', benchmark_memo)
