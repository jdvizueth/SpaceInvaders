"""
Subcontroller module for Alien Invaders

This module contains the subcontroller to manage a single level or wave in
the Alien Invaders game.  Instances of Wave represent a single wave. Whenever
you move to a new level, you are expected to make a new instance of the class.

The subcontroller Wave manages the ship, the aliens and any laser bolts on
screen. These are model objects.  Their classes are defined in models.py.

Most of your work on this assignment will be in either this module or
models.py. Whether a helper method belongs in this module or models.py is
often a complicated issue.  If you do not know, ask on Piazza and we will
answer.

Jose Vizueth jdv72
12/7/2021
"""
from game2d import *
from consts import *
from models import *
import random

# PRIMARY RULE: Wave can only access attributes in models.py via getters/setters
# Wave is NOT allowed to access anything in app.py (Subcontrollers are not
# permitted to access anything in their parent. To see why, take CS 3152)


class Wave(object):
    """
    This class controls a single level or wave of Alien Invaders.

    This subcontroller has a reference to the ship, aliens, and any laser bolts
    on screen. It animates the laser bolts, removing any aliens as necessary.
    It also marches the aliens back and forth across the screen until they are
    all destroyed or they reach the defense line (at which point the player
    loses). When the wave is complete, you  should create a NEW instance of
    Wave (in Invaders) if you want to make a new wave of aliens.

    If you want to pause the game, tell this controller to draw, but do not
    update.  See subcontrollers.py from Lecture 24 for an example.  This
    class will be similar to than one in how it interacts with the main class
    Invaders.

    All of the attributes of this class ar to be hidden. You may find that
    you want to access an attribute in class Invaders. It is okay if you do,
    but you MAY NOT ACCESS THE ATTRIBUTES DIRECTLY. You must use a getter
    and/or setter for any attribute that you need to access in Invaders.
    Only add the getters and setters that you need for Invaders. You can keep
    everything else hidden.

    """
    # HIDDEN ATTRIBUTES:
    # Attribute _ship: the player ship to control
    # Invariant: _ship is a Ship object or None
    #
    # Attribute _aliens: the 2d list of aliens in the wave
    # Invariant: _aliens is a rectangular 2d list containing Alien objects or None
    #
    # Attribute _bolts: the laser bolts currently on screen
    # Invariant: _bolts is a list of Bolt objects, possibly empty
    #
    # Attribute _dline: the defensive line being protected
    # Invariant : _dline is a GPath object
    #
    # Attribute _lives: the number of lives left
    # Invariant: _lives is an int >= 0
    #
    # Attribute _time: the amount of time since the last Alien "step"
    # Invariant: _time is a float >= 0s
    #
    # You may change any attribute above, as long as you update the invariant
    # You may also add any new attributes as long as you document them.
    # LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
    #
    #Attribute _right: the attribute that decides whether the aliens move right
    #Invariant: _right is a bool
    #
    #Attribute _rates: the rate in which missiles are fired from the aliens
    #Invariant: _rates is an int
    #
    #Attribute _stepstaken: the number of steps taken by the alien
    #Invariant: _stepstaken is an int
    #
    #Attribute _animator: a coroutine for performing an animation
    #Invariant: _animator is a generator-based coroutine (or None)
    #
    #Attribute _shot: True if the ship has been shot, False otherwise
    #Invariant: _shot is a bool
    #
    #Attribute _end: True if the wave needs to be paused, False otherwise
    #Invariant: _end is a bool
    #
    #Attribute _lives: keeps count of how many lives the ship has
    #Invariant: _lives is an int
    #
    #Attribute _alienslost: True if aliens are all gone, False otherwise
    #Invariant: _alienslost is a bool
    #
    #Attribute _alienswon: True if the aliens have reached the defense line
    #False otherwise
    #Invariant: _alienswon is a bool
    #
    #Attribute _alienspeed: the current number of seconds between alien steps
    #Invariant: _alienspeed is a float > 0 and <= 1

    #GETTERS AND SETTERS GO HERE

    def getEnd(self):
        """
        Get the value of _end
        """
        return self._end

    def getLives(self):
        """
        Gets the value of _lives
        """
        return self._lives

    def setnewShip(self):
        """
        Sets the value of _ship to a new Ship object
        """
        self._ship = Ship()

    def aliensLost(self):
        """
        Gets the value of _alienslost
        """
        return self._alienslost

    def aliensWon(self):
        """
        Gets the value of _alienswon
        """
        return self._alienswon

    def getAlienSpeed(self):
        """
        Gets teh value of the current _alienspeed
        """
        return self._alienspeed

    # INITIALIZER (standard form) TO CREATE SHIP AND ALIENS
    def __init__(self, alienspeed = ALIEN_SPEED, lives = SHIP_LIVES):
        """
        initializes a wave of Alien Invaders
        """
        self._aliens = self.alienlist(ALIEN_ROWS, ALIENS_IN_ROW)
        self._x = 0
        self._ship = Ship()
        self._dline = GPath(points = [0,DEFENSE_LINE,GAME_WIDTH,DEFENSE_LINE], \
        linewidth = 1, linecolor = 'black')
        self._time = 0
        self._right = True
        self._bolts = []
        self._rates = random.randrange(1, BOLT_RATE+1)
        self._stepstaken = 0
        self._animator = None
        self._shot = False
        self._end = False
        self._lives = lives
        self._alienslost = False
        self._alienswon = False
        self._alienspeed = alienspeed

    # UPDATE METHOD TO MOVE THE SHIP, ALIENS, AND LASER BOLTS
    def update(self, input, dt):
        """
        Animates the ship, aliens, and the laser bolts

        Parameter input: which button the player presses
        Precondition: input is a valid GInput object

        Parameter dt: The time in seconds since last update
        Precondition: dt is a number (int or float)
        """
        self.alienmotion(dt)
        self.alienshoot()
        self.lasergone()
        self.alienhit()
        self.shiphit()
        self.alienswonorlost()
        self.shipshoot(input)
        if not self._animator is None:
            try:
                self._animator.send(dt)
            except:
                self._animator = None
                self._ship = None
                self._lives -= 1
                self._shot = False
                self._end = True
        elif self._shot:
            self._animator = self._ship.animateExplosion()
            next(self._animator)
        else:
            self._end = False
            self.shipmotion(input)

    # DRAW METHOD TO DRAW THE SHIP, ALIENS, DEFENSIVE LINE AND BOLTS
    def draw(self, view):
        """
        Initializes the drawing procedure for the wave

        Parameter view: the window in which it will be drawed upon
        Precondition: view is a valid GView object
        """
        for row in self._aliens:
            for alien in row:
                if alien != None:
                    alien.draw(view)
        if self._ship != None:
            self._ship.draw(view)
        self._dline.draw(view)
        for bolt in self._bolts:
            if bolt != None:
                bolt.draw(view)

    # HELPER METHODS FOR COLLISION DETECTION
    def alienhit(self):
        """
        Deletes laser if it hits an alien and sets hit laser to None
        """
        i = 0
        while i < len(self._aliens):
            p = 0
            while p < len(self._aliens[i]):
                j = 0
                while j < len(self._bolts):
                    if self._aliens[i][p] != None and \
                    self._aliens[i][p].collides(self._bolts[j]):
                        self._aliens[i][p] = None
                        del self._bolts[j]
                    else:
                        j += 1
                p += 1
            i += 1

    def shiphit(self):
        """
        if it detects a collision between an enemy laser and the ship it
        removes the bolt from the list and sets _shot to True
        """
        if self._ship != None:
            j = 0
            while j < len(self._bolts):
                if self._ship.collides(self._bolts[j]):
                    del self._bolts[j]
                    self._shot = True
                else:
                    j += 1

    # HELPER METHOD FOR MAKING A 2D LIST WITH ALIENS
    def alienlist(self, rows, inrows):
        """
        creates a 2d list of aliens

        Parameter alienimage: the alien object used in the list
        Precondition: alienimage is a valid Alien object

        Parameter rows: the amount of rows in the list
        Precondition: rows is an int > 1 and < 10

        Parameter inrows: the amount of aliens in each row
        Precondition: inrows is an int > 0
        """
        biglist = []
        alienimage = 0
        sourceimg = ALIEN_IMAGES[0]
        ypos = GAME_HEIGHT - ALIEN_CEILING - (ALIEN_HEIGHT/2) - \
        ((rows-1) * (ALIEN_HEIGHT + ALIEN_V_SEP))
        for n in range(rows):
            xpos = ALIEN_H_SEP + (ALIEN_WIDTH/2)
            smalllist = []
            for n in range(inrows):
                xpos = xpos + (ALIEN_WIDTH) + ALIEN_H_SEP
                smalllist.append(Alien(x = xpos, y =  ypos, width = ALIEN_WIDTH,\
                height = ALIEN_HEIGHT, source = sourceimg))
            biglist.append(smalllist)
            ypos = ypos + (ALIEN_HEIGHT + ALIEN_V_SEP)
            if alienimage >= len(ALIEN_IMAGES) - 1:
                alienimage = 0
            else:
                alienimage = alienimage + 0.5
            if alienimage in (0.0, 0.5):
                sourceimg = ALIEN_IMAGES[0]
            elif alienimage in (1.0, 1.5):
                sourceimg = ALIEN_IMAGES[1]
            elif alienimage in (2.0, 2.5):
                sourceimg = ALIEN_IMAGES[2]
        return biglist

    #HELPER METHOD FOR THE MOTION OF THE SHIP
    def shipmotion(self, input):
        """
        The helper method for moving the ship

        Parameter input: which button the player presses
        Precondition: input is a valid GInput object
        """
        if self._ship != None:
            da = 0
            if input.is_key_down('left'):
                da -= SHIP_MOVEMENT
                self._ship.x = max(self._ship.x + da, SHIP_WIDTH/2)
            if input.is_key_down('right'):
                da += SHIP_MOVEMENT
                self._ship.x = min(self._ship.x + da, GAME_WIDTH - SHIP_WIDTH/2)

    #HELPER METHOD TO DECIDE WHETHER THE SHIP CAN SHOOT
    def shipshoot(self, input):
        """
        decides whether the ship can shoot

        Parameter input: which button the player presses
        Precondition: input is a valid GInput object
        """
        shoot = True
        for bolt in self._bolts:
            bolt.movingbolt()
            if bolt.isPlayerBolt():
                shoot = False
        if shoot:
            self.PlayerBolt(input)
            shoot = False

    #HELPER METHOD THAT ALLOWS SHIP TO SHOOT
    def PlayerBolt(self, input):
        """
        The helper method to shoot the lasers from the player

        Parameter input: which button the player presses
        Precondition: input is a valid GInput object
        """
        if self._ship != None:
            if input.is_key_down('up') or input.is_key_down('spacebar'):
                self._bolts.append(Bolt(self._ship.x, (self._ship.y + \
                (ALIEN_HEIGHT/2) + (BOLT_HEIGHT/2)), BOLT_SPEED, True))

    #HELPER METHOD FOR THE MOTION OF THE ALIENS
    def alienmotion(self, dt):
        """
        The helper method for moving the aliens

        Parameter dt: The time in seconds since last update
        Precondition: dt is a number (int or float)
        """
        mostright = 0
        mostleft = GAME_WIDTH
        if self._time >= self._alienspeed:
            for row in self._aliens:
                for alien in row:
                    if alien != None:
                        if self._right:
                            alien.x += ALIEN_H_WALK
                            mostright = max(mostright, (alien.x + \
                            (ALIEN_WIDTH/2)))
                        else:
                            alien.x -= ALIEN_H_WALK
                            mostleft = min(mostleft, (alien.x - (ALIEN_WIDTH/2)))
            if mostright > (GAME_WIDTH - ALIEN_H_SEP) or mostleft < ALIEN_H_SEP:
                for row in self._aliens:
                    for alien in row:
                        if alien != None:
                            if self._right:
                                alien.x -= ALIEN_H_WALK
                            else:
                                alien.x += ALIEN_H_WALK
                            alien.y -= ALIEN_V_SEP
                self._right = not self._right
            self._time = 0
            self._stepstaken +=1
        else:
            self._time += dt

    #HELPER METHOD THAT ADDS BOLTS FROM ALIENS
    def EnemyBolt(self, alien):
        """
        The helper method that appends bolts from aliens into _bolts

        Parameter alien: which alien is doing the shooting
        Precondition: input is a valid Alien object
        """
        if alien != None:
            self._bolts.append(Bolt(alien.x, alien.y - (ALIEN_HEIGHT/2) - \
            (BOLT_HEIGHT/2), - BOLT_SPEED, False))


    #HELPER METHOD TO DECIDE WHETHER IT IS TIME FOR THE ALIENS TO SHOOT OR NOT
    def alienshoot(self):
        """
        decides if its time for the aliens to shoot
        """
        if self._stepstaken == self._rates:
            self.EnemyBolt(self.chosenalien())
            self._stepstaken = 0
            self._rates = random.randrange(1, BOLT_RATE+1)

    #HELPER METHOD THAT CHOOSES THE SHOOTING ALIEN
    def chosenalien(self):
        """
        decides which alien will be the one shooting
        """
        bigvlist = []
        i = 0
        while i < ALIENS_IN_ROW:
            column = []
            for row in self._aliens:
                if row[i] != None:
                    column.append(row[i])
            i += 1
            bigvlist.append(column)
        lowestaliens = []
        for column in bigvlist:
            if len(column) >= 1:
                bottomalien = column[0]
                for alien in column:
                    if alien.y < bottomalien.y:
                        bottomalien = alien.y
                lowestaliens.append(bottomalien)
            else:
                del bigvlist[bigvlist.index(column)]
        randomalien = lowestaliens[random.randrange(0, len(lowestaliens))]
        return randomalien

    #HELPER METHOD THAT DELETES ANY LASERS OUTSIDE THE WINDOW
    def lasergone(self):
        """
        deletes a laser once it makes it outside the window of the game
        """
        i = 0
        while i < len(self._bolts):
            if self._bolts[i].y > GAME_HEIGHT or (self._bolts[i].y + \
            (BOLT_HEIGHT/2)) < 0:
                del self._bolts[i]
            else:
                i += 1

    def alienswonorlost(self):
        """
        sets _alienswon and _alienslost depending on whether aliens have won or
        lost
        """
        self._alienslost = True
        for row in self._aliens:
            for alien in row:
                if alien != None:
                    self._alienslost = False
                    if (alien.y - (ALIEN_HEIGHT/2)) <= DEFENSE_LINE:
                        self._alienswon = True
