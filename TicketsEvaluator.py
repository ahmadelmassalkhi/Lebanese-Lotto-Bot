from Draw import *

class Ticket:
    def __init__(self, numbers:list[6]) -> None:
        self.numbers = numbers

class TicketsEvaluator:
    def __init__(self, winning_draw:Draw) -> None:
        self.winning_draw = winning_draw
    
    def calculate_correct_numbers(self, ticket:Ticket):
        result = len(set(ticket.numbers) & set(self.winning_draw.result.primary)) # without bonus
        if result == 5 and self.winning_draw.result.bonus in ticket.numbers: print("5 + bonus vvvvvv")
        return result
    
    def evaluate(self, tickets:list[Ticket]):
        for t in tickets:
            print(f'{t.numbers} matched {self.calculate_correct_numbers(t)} numbers !')

    # Function to read predictions from file
    def read_predictions_from_file(self, filePath:str, withBrackets:bool = True):
        tickets = []
        with open(filePath, 'r') as file:
            lines = file.readlines()
            for idx, line in enumerate(lines):
                line = line.strip()
                if not line: continue
                if withBrackets and not line.startswith('[') or not line.endswith(']'): raise ValueError(f"Invalid format at line {idx + 1}")

                # Strip whitespace and remove brackets
                line = line[1:-1].strip()
                if not line: raise ValueError(f"Invalid format at line {idx + 1}")

                # Convert to list of integers
                numbers = list(map(int, line.split(', ')))

                ticket = Ticket(numbers)
                tickets.append(ticket)
        return tickets

if __name__ == "__main__":
    evaluator = TicketsEvaluator(Draw(2242, '2024-08-22', DrawResult([8, 11, 20, 24, 31, 34], 6)))
    evaluator.evaluate(evaluator.read_predictions_from_file('predictions.txt'))