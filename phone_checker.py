import pandas as pd

class PhoneNumberEvaluator:
    def __init__(self):
        self.weights = {
            "تکرار ارقام": 1,
            "ارقام خطی": 1,
            "ارقام آینه ای": 1,
            "ارقام زوج یا فرد": 1,
            "جفت جفت": 1,
            "خوشگفتار": 1,
            "اعداد شانس": 1,
            "الگوهای خاص": 2,
            "اعداد گروهی": 1,
            "تاریخ های خاص": 1,
            "کمیاب": 2
        }

    def repeating_digits(self, number):
        for i in range(len(number)-2):
            if number[i] == number[i+1] == number[i+2]:
                return True
        for i in range(len(number)-3):
            if number[i] == number[i+1] == number[i+2] == number[i+3]:
                return True
        return False

    def sequential_digits(self, number):
        for i in range(len(number)-2):
            a, b, c = int(number[i]), int(number[i+1]), int(number[i+2])
            if b == a+1 and c == b+1:
                return True
            if b == a-1 and c == b-1:
                return True
        return False

    def mirror_digits(self, number):
        return number == number[::-1]

    def even_or_odd(self, number):
        if all(int(d) % 2 == 0 for d in number):
            return True
        if all(int(d) % 2 == 1 for d in number):
            return True
        return False

    def double_pairs(self, number):
        for i in range(len(number)-3):
            if number[i] == number[i+1] and number[i+2] == number[i+3]:
                return True
        return False

    def easy_to_remember(self, number):
        return self.repeating_digits(number) or self.sequential_digits(number) or self.double_pairs(number)

    def lucky_numbers(self, number):
        lucky_digits = {'7','8','9'}
        return any(d in lucky_digits for d in number)

    def vip_pattern(self, number):
        return number.startswith("09") and (self.repeating_digits(number) or self.sequential_digits(number))

    def grouped_numbers(self, number):
        return self.double_pairs(number)

    def special_dates(self, number):
        years = ['137','138','139','140'] # examples
        return any(number.startswith(y) for y in years)

    def rarity(self, number):
        common_patterns = ['123', '000', '111', '222', '333', '444', '555', '666', '777', '888', '999'] # examples
        return not any(p in number for p in common_patterns)

    def evaluate_number(self, number):
        features = {
            "تکرار ارقام": self.repeating_digits(number),
            "ارقام خطی": self.sequential_digits(number),
            "ارقام آینه ای": self.mirror_digits(number),
            "ارقام زوج یا فرد": self.even_or_odd(number),
            "جفت جفت": self.double_pairs(number),
            "خوشگفتار": self.easy_to_remember(number),
            "اعداد شانس": self.lucky_numbers(number),
            "الگوهای خاص": self.vip_pattern(number),
            "اعداد گروهی": self.grouped_numbers(number),
            "تاریخ های خاص": self.special_dates(number),
            "کمیاب": self.rarity(number)
        }

        score = sum(self.weights[f]*v for f,v in features.items())
        features["امتیاز"] = score
        features["شماره"] = number
        return features

    def evaluate_score_list(self, numbers_list):
        results = [self.evaluate_number(num) for num in numbers_list]
        df = pd.DataFrame(results)

        for key in self.weights.keys():
            df[key] = df[key].replace({True: 'دارد', False: 'ندارد'})

        print(f"scores set successfully")
        return df