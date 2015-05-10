import random
import copy
import Ring
import Vector

# Set the Game Theory Payoff Matrix
# Prisoner's Dilemma payoff matrix lookup w/ 3 options: Cooperate, Defect, Suicide (for removing null programs).
suicideCost = -1000
Prisoners = { ('C','C'):Vector.Vector([ 0.75, 0.75 ]) , \
              ('C','D'):Vector.Vector([ 0.00, 1.00 ]) , \
              ('D','C'):Vector.Vector([ 1.00, 0.00 ]) , \
              ('D','D'):Vector.Vector([ 0.00, 0.00 ]) , \
              ('X','C'):Vector.Vector([ suicideCost, 1.00 ]) , \
              ('X','D'):Vector.Vector([ suicideCost, 1.00 ]) , \
              ('C','X'):Vector.Vector([ 1.00, suicideCost ]) , \
              ('D','X'):Vector.Vector([ 1.00, suicideCost ]) , \
              ('X','X'):Vector.Vector([ suicideCost, suicideCost ]) }
print "('C','C') = " + str(Prisoners[('C','C')])
print "('C','D') = " + str(Prisoners[('C','D')])
print "('D','C') = " + str(Prisoners[('D','C')])
print "('D','D') = " + str(Prisoners[('D','D')])

# Allow nondeterministic players
ALLOW_RANDOM = False
# Allow genome to make the interpreter move along the genome a number of steps
ALLOW_FWD_JUMPS  = False
ALLOW_BACK_JUMPS  = True

def GenomeInterpreter( genome, opLastMove, turn=1, depth=0 ):
    """
    This function reads instructions off a ring object and returns the instructions off that ring to a game engine.
    """
    # If in an unending loop looking for an instruction then return a response that will be punished.
    if depth > 50:
        return 'X'
    # If not to deep then go on...
    genome.turn(turn)
    instruction = genome.first()
    # This try is here to handle jumps in the genome to another index by turning the genome ring
    try:
        return GenomeInterpreter( genome, opLastMove, int(instruction), depth+1 )
    # If the instruction isn't a number then it's an instruction so do it!
    except ValueError:
        if instruction == 'P':
            return opLastMove
        elif instruction == 'Q':
            moves = ['C','D']
            if opLastMove == 'X':
                return 'X'
            moves.remove(opLastMove)
            return moves[0]
        elif instruction == 'R':
            return random.choice(['C','D'])
        else:
            return instruction   

def GameEngine(p1, p2, rounds=1):
    """
    This plays a game w/ two players.  The results of each players single move (either C to cooperate
    or D to defect) and returns a vector, a slightly modified list, with each players payout.  There is 
    a third move in the payoff matrix which is an illegal move, denoted by X, w/ a severe penalty.
    It's used for handling error cases or invalid player programs by the GenomeInterpreter.
    """
    
    # Prime the game so they start from the 1st position on the genome ring.
    p1.turn(-1)
    p2.turn(-1)
    p2LastMove = 'X' # Punish a starting move that asks for a nonexistant previous move.
    p1LastMove = 'X'
    score = Vector.Vector([0,0])
    # Now play the rest
    for i in range(rounds):
        p1Move = GenomeInterpreter(p1, p2LastMove)
        p2Move = GenomeInterpreter(p2, p1LastMove)
        score = score + Prisoners[(p1Move,p2Move)]
        p1LastMove = p1Move
        p2LastMove = p2Move
    return score

def RandomBase():
    """
    Returns one of the possible instuctions that could form a player program.
    """
    # Defines how far a jump instruction can go.
    jumpLimit = 9 # I limit this to 9 so I can tell the string form of '-11' from '-1' then '1'
    choiceList = ['C','D','P','Q']
    if ALLOW_RANDOM:
	choiceList.append('R')
    if ALLOW_BACK_JUMPS:
	choiceList.append(random.randint(-jumpLimit,-1))
    if ALLOW_FWD_JUMPS:
        choiceList.append(random.randint(2,jumpLimit))
    return random.choice(choiceList)

def GenomeStr(genome):
    """
    Returns the contents of an iterateable object like a ring that stores a players program as a string.
    """
    return ''.join(map(lambda x: str(x), genome))

#############################
# Start of the main program #

# The number of members in the population.
popSize = 60
print "Population size: " + str(popSize)
# The number of population members allowed to reproduce into the next generation.
breeders = int( 0.7 * popSize )
print "Breeders per generation: " + str(breeders)
#Mutation probability
mutationChance = 0.01
print "Mutation Probability: " + str(mutationChance)
# Max length genome for any individual in intial population
maxInitGenomeLen = 50
# Max length gemone for any individual at any time.
maxLenGenome = 50
# Maximum number of generation to evolve the population over
maxGenerations = 1000
# Print Genomes?
debugGenomes = True
numDebugGenomes = 5

# Initialize the population...
print "Initializing the population"
population = []
for i in range(popSize):
    # Add the individual to the population and their starting fitness of zero.  Form of [fitness, genome]
    population.append([0, Ring.Ring([random.choice(['C','D'])] + \
        [RandomBase() for i in range(random.randint(0,maxInitGenomeLen))])]) # Sets the rest of the player.

print "Beginning Evolution!"

# Evolve until the halt criteria is met.
for j in range(maxGenerations):
        
    # Reset fitness scores for this round
    for individual in population:
        individual[0] = 0.0
        
    # Mutate some survivors
    for individual in population:
        for base in range(len(individual[1])):
            if random.random() < mutationChance:
                individual[1][base] = RandomBase()

    # Do crossover reproduction
    for i in range(popSize-len(population)):
        # Select parents
        p1 = random.choice(population)[1]
        p2 = random.choice(population)[1]
        # Make the child program
        kid = p1[:random.randint(0,len(p1)-1)]
        kid.extend(p2[random.randint(0,len(p2)-1):])
        # Limit genome size by slicing off anything beyond a predefined limit to prevent bloat
        kid = kid[:maxLenGenome]
        population.append([0.0,Ring.Ring(kid)]) 

    # Compete 
    # randomly select the number of iterations played for each generation.
    rounds = random.randint(10,20)     
    # Randomly pair up competitors.
    pairings = 10 # Test against multiple others to get a better idea of global fitness.
    norm = [0]*popSize
    for p1 in range(popSize):
        for p2 in range(pairings):
            #p2 = random.randint(0,popSize-1)
            # Use the copy method here so the originals aren't modified
            scoreboard = GameEngine( copy.copy(population[p1][1]), copy.copy(population[p2][1]), rounds)
            population[p1][0] += scoreboard[0]
            population[p2][0] += scoreboard[1]
            norm[p1] += rounds
            norm[p2] += rounds
    
    # Normalize scores
    for i in range(popSize):
        population[i][0] = population[i][0] / norm[i]
        
    # Population sorting
    population.sort(reverse=True)
        
    # Population stats
    bestScore = population[0][0]
    count = 0
    meanScore = 0
    for individual in population:
        if individual[0] >= 0:
            count += 1
            meanScore += individual[0]
    population = population[:count] # Get rid of all the individuals with a negative score
    worstScore = population[:count][-1][0]
    meanScore = meanScore/count

    # Cull the herd
    population = population[:breeders]

    # Debug what's going on
    print 'Generation: ' + str(j) + \
          '\tBest: ' + '%5.3f'%bestScore + \
          '\tMean: ' + '%5.3f'%meanScore + \
          '\tWorst: ' + '%5.3f'%worstScore + \
          '\tViable: ' + '%5.3f'%(float(count)/popSize)
    if debugGenomes:
        for i in range(numDebugGenomes):
            print '\tscore: ' + '%5.3f'%population[i][0] + ' by ' + GenomeStr(population[i][1])
    
# Inform of normal exit
print "Program Completed Normally"
