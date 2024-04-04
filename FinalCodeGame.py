import sys
import numpy as np
from prettytable import PrettyTable
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout, QPushButton, QTextEdit, QInputDialog
from PyQt5.QtGui import QFont



class GameSolverApp(QWidget):
    def __init__(self):
        super().__init__()

        self.num_strategies_player1 = 0
        self.num_strategies_player2 = 0
        self.strategies_player1 = []
        self.strategies_player2 = []
        self.normal_form_game = []

        self.initUI()


    def initUI(self):
        self.setWindowTitle("Game Theory with PyQt5")
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout()

        self.lbl_player1 = QLabel("Enter the number of strategies for Player 1:")
        self.layout.addWidget(self.lbl_player1)

        self.input_player1 = QLineEdit()
        self.layout.addWidget(self.input_player1)

        self.lbl_player2 = QLabel("Enter the number of strategies for Player 2:")
        self.layout.addWidget(self.lbl_player2)

        self.input_player2 = QLineEdit()
        self.layout.addWidget(self.input_player2)

        self.btn_create_game = QPushButton("Create Game")
        self.layout.addWidget(self.btn_create_game)

        self.result_text = QTextEdit()
        self.layout.addWidget(self.result_text)

        self.btn_create_game.clicked.connect(self.create_game)

        self.setLayout(self.layout)

    


    def create_game(self):
        self.num_strategies_player1 = int(self.input_player1.text())
        self.num_strategies_player2 = int(self.input_player2.text())

        self.strategies_player1 = []
        self.strategies_player2 = []
        self.normal_form_game = []

        for i in range(self.num_strategies_player1):
            strategy1, ok1 = QInputDialog.getText(self, "Strategy Input", f"Enter the name for Strategy {i + 1} for Player 1:")
            if ok1:
                self.strategies_player1.append(strategy1)

        for i in range(self.num_strategies_player2):
            strategy2, ok2 = QInputDialog.getText(self, "Strategy Input", f"Enter the name for Strategy {i + 1} for Player 2:")
            if ok2:
                self.strategies_player2.append(strategy2)

        for _ in range(self.num_strategies_player1):
            row = []
            for _ in range(self.num_strategies_player2):
                row.append([0, 0])
            self.normal_form_game.append(row)

        self.collect_payoff_data()

    def collect_payoff_data(self):
        for s1 in range(self.num_strategies_player1):
            for s2 in range(self.num_strategies_player2):
                strategy1 = self.strategies_player1[s1]
                strategy2 = self.strategies_player2[s2]
                payoff_player1, ok1 = self.get_payoff(f"Enter the gain for {strategy1} vs {strategy2} for Player 1:")
                payoff_player2, ok2 = self.get_payoff(f"Enter the gain for {strategy1} vs {strategy2} for Player 2:")

                if ok1 and ok2:
                    self.normal_form_game[s1][s2][0] = payoff_player1
                    self.normal_form_game[s1][s2][1] = payoff_player2

        self.display_normal_form_game()
        self.eliminate_equal_strategies()  
        self.eliminate_dominee_strategies()

    def get_payoff(self, prompt):
        payoff, ok = QInputDialog.getInt(self, "Payoff Input", prompt)
        return payoff, ok

    def display_normal_form_game(self):
        table = PrettyTable()
        table.field_names = [" ", *self.strategies_player2]

        for i in range(self.num_strategies_player1):
            row = [self.strategies_player1[i]]
            for j in range(self.num_strategies_player2):
                payoff1, payoff2 = self.normal_form_game[i][j]
                row.append(f"({payoff1}, {payoff2})")
            table.add_row(row)

        self.result_text.clear()
        self.result_text.append("The Normal Form Game")
        self.result_text.append(table.get_string())

    def eliminate_equal_strategies(self):
        matrix = np.array(self.normal_form_game)
        while True:
            p1, p2 = self.extract_payoff_matrices(matrix)
            tabE1 = self.eliminate_equal_lines(p1)
            tabE2 = self.eliminate_equal_columns(p2)
            matrix = self.delete_rows_and_columns(matrix, tabE1, tabE2)
            self.strategies_player1 = self.remove_elements(self.strategies_player1, tabE1)
            self.strategies_player2 = self.remove_elements(self.strategies_player2, tabE2)
            if not tabE1 and not tabE2:
                break

        self.display_updated_game_after_eliminating_equal(matrix, self.strategies_player1, self.strategies_player2)


    def eliminate_equal_lines(self, matrix):
        lines_to_eliminate = []
        num_rows = len(matrix)

        for i in range(num_rows):
            if i in lines_to_eliminate:
                continue
            for j in range(i + 1, num_rows):
                if np.array_equal(matrix[i], matrix[j]):  
                    lines_to_eliminate.append(j)

        return lines_to_eliminate

    def eliminate_equal_columns(self, matrix):
        columns_to_eliminate = []
        num_rows = len(matrix)
        num_cols = len(matrix[0])

        for i in range(num_cols):
            if i in columns_to_eliminate:
                continue
            for j in range(i + 1, num_cols):
                column_i = [matrix[row][i] for row in range(num_rows)]
                column_j = [matrix[row][j] for row in range(num_rows)]
                if np.array_equal(column_i, column_j): 
                    columns_to_eliminate.append(j)

        return columns_to_eliminate

    def eliminate_dominee_strategies(self):
        matrix = np.array(self.normal_form_game)
        while True:
            p1, p2 = self.extract_payoff_matrices(matrix)
            tab1 = self.find_dominated_rows(p1)
            tab2 = self.find_dominated_columns(p2)
            matrix = self.delete_rows_and_columns(matrix, tab1, tab2)
            self.strategies_player1 = self.remove_elements(self.strategies_player1, tab1)
            self.strategies_player2 = self.remove_elements(self.strategies_player2, tab2)
            if not tab1 and not tab2:
                break

        self.display_updated_game_after_eliminating_dominated(matrix, self.strategies_player1, self.strategies_player2)


    def extract_payoff_matrices(self, matrix):
        num_rows = len(matrix)
        num_columns = len(matrix[0])

        player1_payoffs = []
        player2_payoffs = []

        for i in range(num_rows):
            player1_row = []
            player2_row = []

            for j in range(num_columns):
                payoff = matrix[i][j]
                player1_payoff, player2_payoff = payoff
                player1_row.append(player1_payoff)
                player2_row.append(player2_payoff)

            player1_payoffs.append(player1_row)
            player2_payoffs.append(player2_row)

        return player1_payoffs, player2_payoffs

    def find_dominated_rows(self, matrix):
        dominated_indices = []
        num_rows = len(matrix)
        for i in range(num_rows):
            is_dominated = False
            for j in range(num_rows):
                if i == j:
                    continue
                if all(matrix[j][k] > matrix[i][k] for k in range(len(matrix[i]))):
                    is_dominated = True
                    break
            if is_dominated:
                dominated_indices.append(i)
        return dominated_indices
    
    def find_dominated_columns(self, matrix):
        transposed_matrix = [[matrix[j][i] for j in range(len(matrix))] for i in range(len(matrix[0]))]
        dominated_indices = []
        num_columns = len(transposed_matrix)
        for i in range(num_columns):
            is_dominated = False
            for j in range(num_columns):
                if i == j:
                    continue
                if all(transposed_matrix[j][k] > transposed_matrix[i][k] for k in range(len(transposed_matrix[i]))):
                    is_dominated = True
                    break
            if is_dominated:
                dominated_indices.append(i)

        return dominated_indices
    
    def display_updated_game_matrix(self, matrix, player1_labels, player2_labels, title):
        num_strategies_player1 = len(player1_labels)
        num_strategies_player2 = len(player2_labels)

        table = PrettyTable()
        table.field_names = [" ", *player2_labels]

        for i in range(num_strategies_player1):
            row = [player1_labels[i]]
            for j in range(num_strategies_player2):
                payoff1, payoff2 = matrix[i][j]
                row.append(f"({payoff1}, {payoff2})")
            table.add_row(row)

        self.result_text.append(title)
        self.result_text.append(table.get_string())
        self.result_text.append("-----------------------------------------")

    def display_updated_game_after_eliminating_equal(self, matrix, player1_labels, player2_labels):
        title = "Updated Normal Form after eliminating equivalent strategies "
        self.display_updated_game_matrix(matrix, player1_labels, player2_labels, title)

    def display_updated_game_after_eliminating_dominated(self, matrix, player1_labels, player2_labels):
        title = "Updated Normal Form after eliminating dominated strategies:"
        self.display_updated_game_matrix(matrix, player1_labels, player2_labels, title)

    def delete_rows_and_columns(self, matrix, rows_to_delete, columns_to_delete):
        selected_rows = np.delete(matrix, rows_to_delete, axis=0)
        selected_columns = np.delete(selected_rows, columns_to_delete, axis=1)
        return selected_columns

    def remove_elements(self, list1, indices_to_remove):
        modified_list = [elem for i, elem in enumerate(list1) if i not in indices_to_remove]
        return modified_list

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GameSolverApp()
    ex.show()
    sys.exit(app.exec_())

