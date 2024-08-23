import os
from pathlib import Path


class DrawResult:
    def __init__(self, primary:list[6], bonus:int) -> None:
        self.primary = primary
        self.bonus = bonus


class Draw:
    def __init__(self, number: int, date: str, result: DrawResult) -> None:
        self.number = number
        self.date = date
        self.result = result

    def to_string(self, with_bonus:bool = True):
        result_str = ','.join(map(str, self.result.primary))
        if with_bonus: return f"{self.number}, {self.date}, [{result_str}], {self.result.bonus}"
        return f"{self.number}, {self.date}, [{result_str}]"


class DrawSaver:
    def __init__(self) -> None:
        self.RESULT_DIR_PATH = './draw_history'
        self.JOINED_OUTPUT_PATH = self.RESULT_DIR_PATH + '/draw_history.txt'

    def save_draws(self, year: int, draws: list[Draw]):
        # Ensure the directory exists; if not, create it
        result_dir = Path(self.RESULT_DIR_PATH)
        result_dir.mkdir(parents=True, exist_ok=True)

        # Open the file in write mode
        with open(result_dir / f'{year}.txt', 'w') as file:
            for draw in draws:
                file.write(draw.to_string(False) + '\n')

    def save_draws_dict(self, draws: dict):
        for year in draws.keys():
            self.save_draws(year, draws[year])

    def join_draw_files(self):
        files = os.listdir(self.RESULT_DIR_PATH)

        with open(self.JOINED_OUTPUT_PATH, 'w') as outfile:
            for file in files:
                if file.endswith('.txt'):
                    # skip if not a valid year-results .txt file
                    file_stem = os.path.splitext(os.path.basename(file))[0]  # Get filename without extension
                    if not self.is_valid_filestem(file_stem): continue

                    # copy content into output-file
                    file_path = os.path.join(self.RESULT_DIR_PATH, file)
                    with open(file_path, 'r') as infile:
                        outfile.write(f"Content of {file}:\n")
                        outfile.write(infile.read())
                        outfile.write("\n\n")
        print(f"Contents of all .txt files have been written to {self.JOINED_OUTPUT_PATH}")

    def is_valid_filestem(self, stem:str):
        try:
            int(stem)
            return len(stem) == 4
        except ValueError:
            return False
