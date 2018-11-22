import json
import utilities as util
import operator

file_string = 'json/stats.json'

class Stats:
    def __init__(self):
        self.stats = util.load_file(file_string)
        self.ops = {"+": operator.iadd,
                    "-": operator.isub,}


    def change_stat(self, trick: str, status: str, op: str) -> str:
        if trick not in self.stats:
            return 'i am not keeping stats for that trick.'
        values = self.to_int(self.stats[trick])
        if status == 'success':
            values['success'] = self.ops[op](values['success'], 1)
        values['total'] = self.ops[op](values['total'], 1)
        self.stats[trick] = self.to_string(values)
        rstring = f'{trick} stat updated to: {values["success"]} successes | {values["total"] - values["success"]} fails | {values["total"]} attempts'
        return rstring


    def to_int(self, target: str) -> dict:
        temp = target.split('/')
        for x in range(len(temp)):
            temp[x] = int(temp[x])
        return {'success': temp[0], 'total': temp[1]}


    def to_string(self, target: dict) -> str:
        return f'{target["success"]}/{target["total"]}'


    def get_stat(self, trick: str) -> str:
        if trick not in self.stats:
            return 'i am not keeping stats for that trick.'
        values = self.to_int(self.stats[trick])
        return f'{trick} stats: {values["success"]} successes | {values["total"] - values["success"]} fails | {values["total"]} attempts'

    def get_tricks(self) -> str: 
        return ', '.join(self.stats.keys())


    def save(self):
        util.write_file(file_string, self.stats)