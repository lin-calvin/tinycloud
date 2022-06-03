import email.utils
import datetime
import math
def calc_size(size:str):
    """
    Claculate size from a string
    """
    B=1
    K=1024
    M=K*1024
    G=K*1024
    return eval(str(int(size[:-1]))+"*"+size[-1])
def time_as_rfc(timestamp:int):
    """
    Convert timestamp to RFC2822 format
    """
    return email.utils.format_datetime( datetime.datetime.fromtimestamp(timestamp))
debug=1
class log():
    @staticmethod
    def box_message(txt):
        if len(txt)<15:
            a=math.floor((15-len(txt))/2)
            a=" "*a
            txt=a+txt+a
        print("#"*(len(txt)+2))
        print("#"+txt+"#")
        print("#"*(len(txt)+2))
