import random
import string
import matplotlib.pyplot as plt
import pandas as pd 



#This function starts off with an empty string and generates random lower case letters up till key legnth amount of times 
#After that those chars are joined and that is the chromosome
#The Chromosome is then addded to the population

# param(key_length): length of the chromosome/key
# param(population_size): Number of chromosomes we will have
def initialize_population(key_length, population_size):
    population = []
    for _ in range(population_size):
        chromosome = ''.join(random.choices(string.ascii_lowercase, k=key_length)) # ensure that only lowercase letters are used
        population.append(chromosome)
    return population





#Took from chatGPT assuming that decryption was not part of the assignment
def decrypt(key, encrypted_text):
    decrypted_text = ""
    key_length = len(key)
    key_as_int = [ord(i) - ord('a') for i in key] # normalize to 0-25
    ciphertext_int = [ord(i) - ord('a') for i in encrypted_text] # normalize to 0-25
    for i in range(len(ciphertext_int)):
        value = (ciphertext_int[i] - key_as_int[i % key_length]) % 26
        decrypted_text += chr(value + ord('a')) # convert back to letter
    return decrypted_text


#This is the fitness function, we are decrypting the text using our chromosome as the key.
# We have the expected frequency of each letter in an array and we will check to see if our decrypted text matches the frequency
# The closer the match the higher the fitness

# param(chromosome): possible key and will be used to decrypt the text
# param(encrypted_text): encrypted 
def fitness(key, encrypted_text):
    expected_frequencies = [
        0.085, 0.016, 0.0316, 0.0387, 0.121, 0.0218, 0.0209, 0.0496,
        0.0733, 0.0022, 0.0081, 0.0421, 0.0253, 0.0717, 0.0747, 0.0207,
        0.001, 0.0633, 0.0673, 0.0894, 0.0268, 0.0106, 0.0183, 0.0019,
        0.0172, 0.0011
    ]

    cipher = encrypted_text.lower()
    cipher = ''.join(filter(str.isalpha, cipher))

    ke = key.lower()
    ke = ''.join(filter(str.isalpha, ke))

    key_offsets = [ord(char) - ord('a') for char in ke]

    cipher_int = [(ord(char) - ord('a')) for char in cipher]
    plain = [(26 + cipher_int[i] - key_offsets[i % len(key_offsets)]) % 26 for i in range(len(cipher_int))]

    char_count = [0] * 26

    for char in plain:
        char_count[char] += 1

    total_chars = sum(char_count)
    score = 0

    for i in range(len(char_count)):
        frequency = char_count[i] / total_chars
        score += abs(frequency - expected_frequencies[i])

    return score 


#The code picks k random chromosomes from the population and measures their fitness. The fitter one or the one with the lowest fitness value is chosen 
#To be the parents

#param(k):Number of parents
#param(population):Population of chromosomes
#param(encrypted_text):Encrpted text used to measure the fitness of the chromosome
def tournament_selection(k, population, encrypted_text):
    #randomly select 2 from population array
    parents = []

    for i in range (2):
        competitors = random.sample([competitor for competitor in population if competitor not in parents], k)        
        competitors.sort(key=lambda x: fitness(x, encrypted_text))
        parents.append(competitors[0])
    return parents


#Crossover function. It is a one point crossover

#param(population):Population of chromosomes
#param(encrypted_text):Encrypred text to measure the fitness of the chromosome
#param(crossover_rate):Rate at which crossover happens
def crossover(population, encrypted_text, crossover_rate, k):
    offspring = []
    if random.random() < crossover_rate:  # Use random.random() for probability
        parent1, parent2 = tournament_selection(k, population, encrypted_text)
        crossover_point = random.randint(1, min(len(parent1), len(parent2)))  # Choose a safe crossover point
        offspring1 = parent1[:crossover_point] + parent2[crossover_point:]
        offspring2 = parent2[:crossover_point] + parent1[crossover_point:]
        offspring.append(offspring1)
        offspring.append(offspring2)
    else:
        # If no crossover, select random parents to pass on their genes
        offspring.extend(tournament_selection(k, population, encrypted_text))
    return offspring


#The fittest individual/individuals are chosen to go to the next generation to ensure the best solution is not lost
#param(population):Population of chromosomes
#param(encrypted_text):Encrypted text used to measure fitness 
#param(k):Number of elites to move on to the next generation
def elitism(population, encrypted_text, k):
    # Evaluate the fitness of each chromosome in the population
    scored_population = [(chromosome, fitness(chromosome, encrypted_text)) for chromosome in population]
    # Sort the population by fitness score in ascending order (lower is better)
    scored_population.sort(key=lambda x: x[1])
    # Select the top 'k' individuals with the best (lowest) fitness scores
    elite_individuals = [chromosome for chromosome, score in scored_population[:k]]
    return elite_individuals



    

#This function chooses a random position of the key and changes one of the chars into a random char

#param(mutation_rate):Rate at which mutation occurs
#param(offspring):Offspring to be mutated
def mutate(mutation_rate, offspring):
    # Use random.random() for mutation probability
    if random.random() < mutation_rate:
        offspring_list = list(offspring)
        random_position = random.randint(0, len(offspring) - 1)
        offspring_list[random_position] = random.choice(string.ascii_lowercase)
        offspring = ''.join(offspring_list)
    return offspring
    


#Implementation of genetic algorithm it uses all of the above function to evolve a key for an encryption 

#param(encrypted_text):Encrypted text that we are trying to decrypt 
#param(generations):The number of iterations our genetic algorithm will run for 
#param(mutation_rate):The rate at which mutation occurs
#param(crossover_rate):Rate at which crossover happens
#param(key_length):Desired length of the key
#param(population_size):Number of generated chromosomes
#param(k):Number of parents to be chosen for crossover

generations_count = []
fitness_values =[]

def genetic_algorithm(encrypted_text, generations, mutation_rate, crossover_rate, key_length, population_size, k):
    population = initialize_population(key_length, population_size)

    for generation in range(generations):
        elites = elitism(population, encrypted_text, 2)
        new_population = elites.copy()


        # Make sure to fill the population up to the population size
        while len(new_population) < population_size:
            # Create two new offspring
            offspring = crossover(population, encrypted_text, crossover_rate,k)

            # Mutate the offspring and add them to the new population
            for child in offspring:
                mutated_child = mutate(mutation_rate, child)
                new_population.append(mutated_child)
                # Break if we've reached the desired population size
                if len(new_population) >= population_size:
                    break

        # The new generation replaces the old one
        population = new_population[:population_size]  # Ensure the population size remains constant

        # Find and print the best solution in the current generation
        best_individual = min(population, key=lambda x: fitness(x, encrypted_text))
        generations_count.append(generation)
        fitness_values.append(fitness(best_individual,encrypted_text))
        print(f"Generation {generation}: Best Fitness = {fitness(best_individual, encrypted_text)}, Best Key = {best_individual}")
    # Return the best individual found in the final generation
    return min(population, key=lambda x: fitness(x, encrypted_text))





#Edit this seed and the change the number in data.txt to choose which file 
#
random.seed(950) 

with open('Data2.txt', 'r') as file:
    # Read the first line and convert it to an integer to get the key length
    key_length = int(file.readline().strip())
    
    # Read the rest of the file and save it as encrypted text
    encrypted_text = file.read()
#Change these parameters to test different configurationg
    print(genetic_algorithm(encrypted_text,200,0.2,1,key_length,200,5))

    df = pd.DataFrame({
        'Generations': generations_count,
        'Fitness': fitness_values
    })
    df.to_excel('Data.xlsx', index=False)

