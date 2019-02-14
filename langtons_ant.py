import numpy as np
import re
import sys
import matplotlib.pyplot as plt
import matplotlib as mpl

dimen_x = 125
dimen_y = 125
maxiter = 90000000
num_ants = 1
face_direction = [0]
rules = ['rllrnnnnnnnnnnnnnnnn']
antstate = 0
xpos = [int(dimen_x/2)]
ypos = [int(dimen_y/2)]
nstates = len(rules[0])
geometry = 'finite'
antstates = len(rules) - 1

def checkrule(string, search=re.compile(r'[^lnru]').search):

    return not bool(search(string))


def main(argv):

    for rule in rules:
        if not checkrule(rule):
            sys.exit('Invalid rule. Exiting.')

    # create grid and ants
    grid = Grid(dimen_x, dimen_y, geometry)
    ants = []
    for i in range(num_ants):
        ants.append(Ant(face_direction[i], xpos[i], ypos[i], rules, nstates, antstates))

    for i in np.arange(maxiter):
        # loop over ants (in case there's more than one)
        grid, ants = update(grid, ants, i, antstates)
        #grid.final_plot(ants,i)
    grid.final_plot(ants, maxiter-1)


def update(grid, ants, i, antstates):

    for ant in ants:
        try:
            grid.board= ant.move(grid.board, ant.state, ant.rules)
            if ant.state == antstates:
                ant.state = 0
            else:
                ant.state = ant.state + 1
        except:
            # general error handling: just quit, write debug msg
            grid.final_plot(ants, i)
            sys.exit("Something weird is going on")

        # check geometry to make sure we didn't fall off a cliff, quit if we did
        # for other topologies, apply boundary conditions
        if not grid.check_geometry(ant.position):
            # end the simulation if the ant hits the wall
            grid.final_plot(ants, i)
            sys.exit("Ant fell off the map at timestep = %d!" % i)

    return grid, ants


class Grid:

    def __init__(self, dimen_x, dimen_y, geometry):

        self.dimen = (dimen_x, dimen_y)
        self.geometry = geometry
        self.board = np.zeros((self.dimen[0], self.dimen[1]), dtype=np.int)

    def final_plot(self, ants, step):

        # plot the board state and ants
        # use a mask to make the ant array transparent and overlay only
        # the ants' positions onto the final result
        y = np.zeros((self.dimen[0], self.dimen[1]))
        for ant in ants:
            y[ant.position[0], ant.position[1]] = 1
        y = np.ma.masked_where(y == 0, y)

        # use imshow to print matrix elements using gray colormap. Ants are red.
        plt.imshow(self.board, cmap=plt.get_cmap('plasma_r'), interpolation='none')
        plt.imshow(y, cmap=mpl.cm.jet_r, interpolation='none')
        plt.savefig(rules[0]+'-'+str(num_ants)+'ants'+'-'+str(step+1)+'steps'+'.png')
        plt.show()

    def check_geometry(self, antpos):

        # return true if in valid geometry, flase if ant has fallen off the map
        # also, for non-finite, but bounded geometries, adjust ant position
        check = True
        if self.geometry == 'finite' and (antpos[0] < 0 or antpos[0] > self.dimen[0] or
                                          antpos[1] < 0 or antpos[1] > self.dimen[0]):
            check = False

        return check

class Ant:

    """
    Facing Direction:
         Up              [0,-1]  1
    Left    Right  2 [-1,0]  [1,0]  0
        Down          3  [0,1]
    dirs = [[1,0],[0,-1],[-1,0],[0,1]]
    index of dirs is the face_direction
    Right turn applies cyclic shift in negative direction
    Left turn applies cyclic shift in positive direction
    """

    def __init__(self, face_direction, xpos, ypos, rules, nstates, antstates):

        self.face_direction = face_direction
        self.position = [xpos, ypos]
        self.rules = rules
        self.nstates = nstates
        self.state = 0
        self.antstates = antstates
        self.possiblefacings = ((1, 0), (0, -1), (-1, 0), (0, 1))
        self.geometry = geometry

    def move(self, board, antstate, rules):
        rule = self.rules[antstate]
        # get state of board and current direction
        state = board[self.position[0], self.position[1]]
        directive = rule[state]

        # change the ant's direction
        self.face_direction = self.cycle_dir(directive)

        # cyclically increment the state of the board
        board[self.position[0], self.position[1]] = (state + 1) % self.nstates

        # apply motion based on new direction
        self.position[0] = self.position[0] + self.possiblefacings[self.face_direction][0]
        self.position[1] = self.position[1] + self.possiblefacings[self.face_direction][1]

        return board

    def cycle_dir(self, directive):
        dir_r = (self.face_direction - 1) % len(self.possiblefacings)
        dir_l = (self.face_direction + 1) % len(self.possiblefacings)
        dir_u = (self.face_direction + 2) % len(self.possiblefacings)
        dir_n = self.face_direction

        new_face_direction = None
        # perform a cyclic permutation on the possible facing
        # directions with respect to the movement directive
        if directive == 'r':
            new_face_direction = dir_r
        elif directive == 'l':
            new_face_direction = dir_l
        elif directive == 'u':
            new_face_direction = dir_u
        elif directive == 'n':
            new_face_direction = dir_n

        return new_face_direction


#pretend there's command-line arguments for now
if __name__ == "__main__":
    main(sys.argv[1:])