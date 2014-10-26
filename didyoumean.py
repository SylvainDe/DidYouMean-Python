
import inspect
import dis
import functools

def get_suggestions(var, inspect_frame, lim=10):
    # todo : add distance with coef for locals, glob and builtins
    return (inspect_frame.f_locals.keys() + inspect_frame.f_globals.keys() + inspect_frame.f_builtins.keys())[:lim]

def get_var_name_from_exc(e):
    return e.args[0].split("'")[1]

def didyoumean(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except NameError as e:
            e.args = (e.args[0] +
                    ". Did you mean " +
                    ', '.join(get_suggestions(get_var_name_from_exc(e), inspect.trace()[-1][0])), )
            raise
        except KeyError as e:
            # this will never get any better
            key = (e.args[0] if e.args else '')
            ins = inspect.trace()[-1][0]
            print(ins.f_lasti)
            print(inspect.trace())
            print(dis.dis(ins.f_code))
            e.args = (key, " is not found",)
            raise
        # todo typeerror ?
    return decorated

def func(a, b):
    print("func")
    c = 5
    # c = [5 for i in range(10) if b2 > 0]
    c = b2
    e = {}
    e[3] = 3
    # c = e[2 + 5]


def func2():
    print("func2")
    fun = 2
    func(1, 2)

@didyoumean
def func3():
    print("func3")
    func2()

func3()

