import pykakasi


class ToRoman:
    def __init__(self):
        super().__init__()

    def Roman(self,text):
        romans = ''
        kks = pykakasi.kakasi()
        # text = self.jpn.text()
        result = kks.convert(text)
        # print(result)
        for item in result:
            romans += item['hepburn'].capitalize()
            romans += " "
            print("[{}] ".format(item['hepburn'].capitalize()), end=" ")
        print()
        return romans
