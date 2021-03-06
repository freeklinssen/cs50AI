import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        # print(self.domains)
        self.enforce_node_consistency()
        # print(self.domains)
        self.ac3()
        # print(self.domains)
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for item in self.domains:
            for word in self.crossword.words:
                if item.length != len(word):
                    self.domains[item].remove(word)

        return None

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        overlaps = self.crossword.overlaps

        if overlaps[(x, y)] == None:
            return False

        else:
            overlap = overlaps[(x, y)]
            delete = []

            for word in self.domains[x]:
                equal = 0
                for word2 in self.domains[y]:
                    if word[overlap[0]] == word2[overlap[1]]:
                        equal += 1

                if equal == 0:
                    delete.append(word)

            if len(delete) == 0:
                return False

            else:
                for word in delete:
                    self.domains[x].remove(word)

            return True

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            arcs = []

            for var in self.crossword.variables:
                neighbors = self.crossword.neighbors(var)
                for neighbor in neighbors:
                    arcs.append((var, neighbor))

        changes = 1
        while changes > 0:
            changes = 0
            for item in arcs:
                var1 = item[0]
                var2 = item[1]
                if self.revise(var1, var2) == True:
                    changes += 1

        for item in self.domains:
            if len(self.domains[item]) == 0:
                return False

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.crossword.variables:
            if var not in assignment:
                return False

        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        overlaps = self.crossword.overlaps

        for var in assignment:
            for var2 in assignment:
                if var != var2:
                    if assignment[var] == assignment[var2]:
                        return False
                    
            if var.length != len(assignment[var]):
                return False

            neighbors = self.crossword.neighbors(var)
            for neighbor in neighbors:
                if neighbor in assignment:
                    overlap = overlaps[(var, neighbor)]
                    if assignment[var][overlap[0]] != assignment[neighbor][overlap[1]]:
                        return False
                  
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        neighbors = self.crossword.neighbors(var)
        overlaps = self.crossword.overlaps
        List = []
        
        for item in self.domains[var]:
        
            count = 0

            for neighbor in neighbors:
                if neighbor not in assignment:
                    overlap = overlaps[(var, neighbor)]

                    for word in self.domains[neighbor]:
                        if item[overlap[0]] != word[overlap[1]]:
                            count += 1
                        
            List.append((item, count))
        
        List = sorted(List, key=lambda count: count[1])
        result = []
        for i in List:
            result.append(i[0])
            
        return result

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        helper = None

        for var in self.crossword.variables:
            if var not in assignment:
                if helper is None:
                    helper = var
                else:
                    domain_var = 0
                    domain_helper = 0
    
                    for item in self.domains[var]:
                        domain_var += 1
                    for item in self.domains[helper]:
                        domain_helper += 1
    
                    if domain_var == domain_helper:
                        if len(self.crossword.neighbors(var)) > len(self.crossword.neighbors(helper)):
                            helper = var
    
                    if domain_var < domain_helper:
                        helper = var

        return helper
        
    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        if self.assignment_complete(assignment):
            
            return assignment

        assign = self.select_unassigned_variable(assignment)

        values = self.order_domain_values(assign, assignment)
        
        if len(values) == 0:
            return None

        for item in values: 
            assignment[assign] = item
            if self.consistent(assignment):
                if self.backtrack(assignment) == assignment:
                    return assignment
                        
        return None
                 
                
def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()

