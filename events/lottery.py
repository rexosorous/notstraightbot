import utilities as util


file_string = 'json/lottery_info.json'

class Lottery:
    def __init__(self):
        self.lottery_dict = util.load_file(file_string)
        self.init_val = 1000
        self.max_ticket_number = 5000

    def get_value(self) -> int:
        return self.lottery_dict['value']

    def get_tickets(self, player: str) -> int:
        # returns how many times the user appears in lottery dict values
        return list(self.lottery_dict.values()).count(player)

    def get_remaining_tickets(self) -> int:
        return self.max_ticket_number - len(self.lottery_dict) + 1

    def user_exists_check(self, player: str) -> bool:
        return player in self.lottery_dict.values()

    def ticket_exists_check(self, number: int) -> bool:
        return str(number) in self.lottery_dict

    def generate_ticket(self) -> int:
        ticket = util.rng(1, self.max_ticket_number)
        while self.ticket_exists_check(ticket):
            ticket = util.rng(1, self.max_ticket_number)
        return ticket

    def buy_tickets(self, player: str, qty: int):
        for _ in range(qty):
            self.lottery_dict[str(self.generate_ticket())] = player
        self.lottery_dict['value'] += qty * 5
        self.save()

    def draw(self) -> str:
        winning_ticket = str(util.rng(1, self.max_ticket_number))
        if winning_ticket in self.lottery_dict:
            winner = self.lottery_dict[winning_ticket]
            return winner
        self.clean_tickets()

    def clean_tickets(self):
        self.lottery_dict = {'value': self.lottery_dict['value']}
        self.save()

    def cleanup(self):
        self.lottery_dict = {'value': self.init_val}
        self.save()

    def save(self):
        util.write_file(file_string, self.lottery_dict)
