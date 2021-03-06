import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }
    #print("people:", people)
    #print("probabilities:", probabilities)
    
    # Loop over all sets of people who might have the trait
    names = set(people)

    #print(powerset(names))
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        
        if fails_evidence:
            continue
        
        #print(powerset(names))
        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            #print("one_gene: ", one_gene)
            for two_genes in powerset(names - one_gene):
                #print("two_genes: ", two_genes)
                
                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    result = {}
    
    for person in people:
        result[person] = {
            "prob": 0,
            "copies": None
        }
        
    #print(result)
    
    for person in people:
        if people[person]["father"] == None and people[person]["mother"] == None:
            if person in one_gene and person not in have_trait:
                result[person]["prob"] = PROBS["gene"][1] * PROBS["trait"][1][False]
                result[person]["copies"] = 1
            elif person in two_genes and person not in have_trait:
                result[person]["prob"] = PROBS["gene"][2] * PROBS["trait"][2][False]
                result[person]["copies"] = 2
            elif person not in two_genes and person not in one_gene and person not in have_trait:  # zero copies of the gene
                result[person]["prob"] = PROBS["gene"][0] * PROBS["trait"][0][False]
                result[person]["copies"] = 0

            elif person in one_gene and person in have_trait:
                result[person]["prob"] = PROBS["gene"][1] * PROBS["trait"][1][True]
                result[person]["copies"] = 1
            elif person in two_genes and person in have_trait:
                result[person]["prob"] = PROBS["gene"][2] * PROBS["trait"][2][True]
                result[person]["copies"] = 2
            elif person not in two_genes and person not in one_gene and person in have_trait:
                result[person]["prob"] = PROBS["gene"][0] * PROBS["trait"][0][True]
                result[person]["copies"] = 0
            
    count = 1 
    while count != 0:
        count = 0
        for person in people:
            if people[person]["father"] != None and people[person]["mother"] != None and result[people[person]["father"]]["copies"] != None and result[people[person]["mother"]]["copies"] != None:
                    
                if person in one_gene and person not in have_trait:
                    if result[people[person]["father"]]["copies"] == 0 and result[people[person]["mother"]]["copies"] == 0:
                        result[person]["prob"] = (PROBS["mutation"] * (1 - PROBS['mutation']) + (1 - PROBS['mutation']) * PROBS["mutation"]) * PROBS["trait"][1][False]
                        result[person]["copies"] = 1
                    elif result[people[person]["father"]]["copies"] == 1 and result[people[person]["mother"]]["copies"] == 1:
                        result[person]["prob"] = ((0.5 - PROBS['mutation']) * (0.5 - PROBS['mutation']) + (0.5 - PROBS['mutation']) * (0.5 - PROBS['mutation'])) * PROBS["trait"][1][False]
                        result[person]["copies"] = 1
                    elif result[people[person]["father"]]["copies"] == 2 and result[people[person]["mother"]]["copies"] == 2:
                        result[person]["prob"] = (PROBS["mutation"] * (1 - PROBS['mutation']) + (1 - PROBS['mutation']) * PROBS["mutation"]) * PROBS["trait"][1][False]
                        result[person]["copies"] = 1
                    elif result[people[person]["father"]]["copies"] == 0 and result[people[person]["mother"]]["copies"] == 1:
                        result[person]["prob"] = ((1 - PROBS['mutation']) * (0.5 - PROBS['mutation']) + PROBS['mutation'] * (0.5 - PROBS['mutation'])) * PROBS["trait"][1][False]
                        result[person]["copies"] = 1
                    elif result[people[person]["father"]]["copies"] == 0 and result[people[person]["mother"]]["copies"] == 2:
                        result[person]["prob"] = ((1 - PROBS['mutation']) * (1 - PROBS['mutation']) + PROBS['mutation'] * PROBS["mutation"]) * PROBS["trait"][1][False]
                        result[person]["copies"] = 1
                    elif result[people[person]["father"]]["copies"] == 1 and result[people[person]["mother"]]["copies"] == 0:
                        result[person]["prob"] = ((1 - PROBS['mutation']) * (0.5 - PROBS['mutation']) + PROBS['mutation'] * (0.5 - PROBS['mutation'])) * PROBS["trait"][1][False]
                        result[person]["copies"] = 1
                    elif result[people[person]["father"]]["copies"] == 1 and result[people[person]["mother"]]["copies"] == 2:
                        result[person]["prob"] = ((0.5 - PROBS["mutation"]) * (1 - PROBS['mutation']) + (0.5 - PROBS['mutation']) * PROBS["mutation"]) * PROBS["trait"][1][False]
                        result[person]["copies"] = 1
                    elif result[people[person]["father"]]["copies"] == 2 and result[people[person]["mother"]]["copies"] == 0:
                        result[person]["prob"] = ((1 - PROBS['mutation']) * (1 - PROBS['mutation']) + PROBS['mutation'] * PROBS["mutation"]) * PROBS["trait"][1][False]
                        result[person]["copies"] = 1
                    elif result[people[person]["father"]]["copies"] == 2 and result[people[person]["mother"]]["copies"] == 1:
                        result[person]["prob"] = ((0.5 - PROBS["mutation"]) * (1 - PROBS['mutation']) + (0.5 - PROBS['mutation']) * PROBS["mutation"]) * PROBS["trait"][1][False]
                        result[person]["copies"] = 1
    
                elif person in two_genes and person not in have_trait:
                    if result[people[person]["father"]]["copies"] == 0 and result[people[person]["mother"]]["copies"] == 0:
                        result[person]["prob"] = PROBS["mutation"] * PROBS['mutation'] * PROBS["trait"][2][False]
                        result[person]["copies"] = 2
                    elif result[people[person]["father"]]["copies"] == 1 and result[people[person]["mother"]]["copies"] == 1:
                        result[person]["prob"] = (0.5 - PROBS['mutation']) * (0.5 - PROBS['mutation']) * PROBS["trait"][2][False]
                        result[person]["copies"] = 2
                    elif result[people[person]["father"]]["copies"] == 2 and result[people[person]["mother"]]["copies"] == 2:
                        result[person]["prob"] = (1 - PROBS["mutation"]) * (1 - PROBS['mutation']) * PROBS["trait"][2][False]
                        result[person]["copies"] = 2
                    elif result[people[person]["father"]]["copies"] == 0 and result[people[person]["mother"]]["copies"] == 1:
                        result[person]["prob"] = PROBS['mutation'] * (0.5 - PROBS['mutation']) * PROBS["trait"][2][False]
                        result[person]["copies"] = 2
                    elif result[people[person]["father"]]["copies"] == 0 and result[people[person]["mother"]]["copies"] == 2:
                        result[person]["prob"] = PROBS['mutation'] * (1 - PROBS['mutation']) * PROBS["trait"][2][False]
                        result[person]["copies"] = 2
                    elif result[people[person]["father"]]["copies"] == 1 and result[people[person]["mother"]]["copies"] == 0:
                        result[person]["prob"] = PROBS['mutation'] * (0.5 - PROBS['mutation']) * PROBS["trait"][2][False]
                        result[person]["copies"] = 2
                    elif result[people[person]["father"]]["copies"] == 1 and result[people[person]["mother"]]["copies"] == 2:
                        result[person]["prob"] = (0.5 -PROBS['mutation']) * (1 - PROBS['mutation']) * PROBS["trait"][2][False]
                        result[person]["copies"] = 2
                    elif result[people[person]["father"]]["copies"] == 2 and result[people[person]["mother"]]["copies"] == 0:
                        result[person]["prob"] = PROBS['mutation'] * (1 - PROBS['mutation']) * PROBS["trait"][2][False]
                        result[person]["copies"] = 2
                    elif result[people[person]["father"]]["copies"] == 2 and result[people[person]["mother"]]["copies"] == 1:
                        result[person]["prob"] = (0.5 -PROBS['mutation']) * (1 - PROBS['mutation']) * PROBS["trait"][2][False]
                        result[person]["copies"] = 2
                        
                elif person not in two_genes and person not in one_gene and person not in have_trait:  # zero copies of the gene
                    if result[people[person]["father"]]["copies"] == 0 and result[people[person]["mother"]]["copies"] == 0:
                        result[person]["prob"] = (1 - PROBS["mutation"]) * (1 - PROBS['mutation']) * PROBS["trait"][0][False]
                        result[person]["copies"] = 0
                    elif result[people[person]["father"]]["copies"] == 1 and result[people[person]["mother"]]["copies"] == 1:
                        result[person]["prob"] = (0.5 - PROBS['mutation']) * (0.5 - PROBS['mutation']) * PROBS["trait"][0][False]
                        result[person]["copies"] = 0
                    elif result[people[person]["father"]]["copies"] == 2 and result[people[person]["mother"]]["copies"] == 2:
                        result[person]["prob"] = (PROBS["mutation"] * PROBS['mutation']) * PROBS["trait"][0][False]
                        result[person]["copies"] = 0
                    elif result[people[person]["father"]]["copies"] == 0 and result[people[person]["mother"]]["copies"] == 1:
                        result[person]["prob"] = (1 - PROBS['mutation']) * (0.5 - PROBS['mutation']) * PROBS["trait"][0][False]
                        result[person]["copies"] = 0
                    elif result[people[person]["father"]]["copies"] == 0 and result[people[person]["mother"]]["copies"] == 2:
                        result[person]["prob"] = (1 - PROBS['mutation']) * PROBS['mutation'] * PROBS["trait"][0][False]
                        result[person]["copies"] = 0
                    elif result[people[person]["father"]]["copies"] == 1 and result[people[person]["mother"]]["copies"] == 0:
                        result[person]["prob"] = (1 - PROBS['mutation']) * (0.5 - PROBS['mutation']) * PROBS["trait"][0][False]
                        result[person]["copies"] = 0
                    elif result[people[person]["father"]]["copies"] == 1 and result[people[person]["mother"]]["copies"] == 2:
                        result[person]["prob"] = PROBS['mutation'] * (0.5 - PROBS['mutation']) * PROBS["trait"][0][False]
                        result[person]["copies"] = 0
                    elif result[people[person]["father"]]["copies"] == 2 and result[people[person]["mother"]]["copies"] == 0:
                        result[person]["prob"] = (1 - PROBS['mutation']) * PROBS['mutation'] * PROBS["trait"][0][False]
                        result[person]["copies"] = 0
                    elif result[people[person]["father"]]["copies"] == 2 and result[people[person]["mother"]]["copies"] == 1:
                        result[person]["prob"] = (0.5 - PROBS['mutation']) * PROBS['mutation'] * PROBS["trait"][0][False]
                        result[person]["copies"] = 0
                    
                elif person in one_gene and person in have_trait:
                    if result[people[person]["father"]]["copies"] == 0 and result[people[person]["mother"]]["copies"] == 0:
                        result[person]["prob"] = (PROBS["mutation"] * (1 - PROBS['mutation']) + (1 - PROBS['mutation']) * PROBS["mutation"]) * PROBS["trait"][1][True]
                        result[person]["copies"] = 1
                    elif result[people[person]["father"]]["copies"] == 1 and result[people[person]["mother"]]["copies"] == 1:
                        result[person]["prob"] = ((0.5 - PROBS['mutation']) * (0.5 - PROBS['mutation']) + (0.5 - PROBS['mutation']) * (0.5 - PROBS['mutation'])) * PROBS["trait"][1][True]
                        result[person]["copies"] = 1
                    elif result[people[person]["father"]]["copies"] == 2 and result[people[person]["mother"]]["copies"] == 2:
                        result[person]["prob"] = (PROBS["mutation"] * (1 - PROBS['mutation']) + (1 - PROBS['mutation']) * PROBS["mutation"]) * PROBS["trait"][1][True]
                        result[person]["copies"] = 1
                    elif result[people[person]["father"]]["copies"] == 0 and result[people[person]["mother"]]["copies"] == 1:
                        result[person]["prob"] = ((1 - PROBS['mutation']) * (0.5 - PROBS['mutation']) + PROBS['mutation'] * (0.5 - PROBS['mutation'])) * PROBS["trait"][1][True]
                        result[person]["copies"] = 1
                    elif result[people[person]["father"]]["copies"] == 0 and result[people[person]["mother"]]["copies"] == 2:
                        result[person]["prob"] = ((1 - PROBS['mutation']) * (1 - PROBS['mutation']) + PROBS['mutation'] * PROBS["mutation"]) * PROBS["trait"][1][True]
                        result[person]["copies"] = 1
                    elif result[people[person]["father"]]["copies"] == 1 and result[people[person]["mother"]]["copies"] == 0:
                        result[person]["prob"] = ((1 - PROBS['mutation']) * (0.5 - PROBS['mutation']) + PROBS['mutation'] * (0.5 - PROBS['mutation'])) * PROBS["trait"][1][True]
                        result[person]["copies"] = 1
                    elif result[people[person]["father"]]["copies"] == 1 and result[people[person]["mother"]]["copies"] == 2:
                        result[person]["prob"] = ((0.5 - PROBS["mutation"]) * (1 - PROBS['mutation']) + (0.5 - PROBS['mutation']) * PROBS["mutation"]) * PROBS["trait"][1][True]
                        result[person]["copies"] = 1
                    elif result[people[person]["father"]]["copies"] == 2 and result[people[person]["mother"]]["copies"] == 0:
                        result[person]["prob"] = ((1 - PROBS['mutation']) * (1 - PROBS['mutation']) + PROBS['mutation'] * PROBS["mutation"]) * PROBS["trait"][1][True]
                        result[person]["copies"] = 1
                    elif result[people[person]["father"]]["copies"] == 2 and result[people[person]["mother"]]["copies"] == 1:
                        result[person]["prob"] = ((0.5 - PROBS["mutation"]) * (1 - PROBS['mutation']) + (0.5 - PROBS['mutation']) * PROBS["mutation"]) * PROBS["trait"][1][True]
                        result[person]["copies"] = 1
                        
                elif person in two_genes and person in have_trait:
                    if result[people[person]["father"]]["copies"] == 0 and result[people[person]["mother"]]["copies"] == 0:
                        result[person]["prob"] = PROBS["mutation"] * PROBS['mutation'] * PROBS["trait"][2][True]
                        result[person]["copies"] = 2
                    elif result[people[person]["father"]]["copies"] == 1 and result[people[person]["mother"]]["copies"] == 1:
                        result[person]["prob"] = (0.5 - PROBS['mutation']) * (0.5 - PROBS['mutation']) * PROBS["trait"][2][True]
                        result[person]["copies"] = 2
                    elif result[people[person]["father"]]["copies"] == 2 and result[people[person]["mother"]]["copies"] == 2:
                        result[person]["prob"] = (1 - PROBS["mutation"]) * (1 - PROBS['mutation']) * PROBS["trait"][2][True]
                        result[person]["copies"] = 2
                    elif result[people[person]["father"]]["copies"] == 0 and result[people[person]["mother"]]["copies"] == 1:
                        result[person]["prob"] = PROBS['mutation'] * (0.5 - PROBS['mutation']) * PROBS["trait"][2][True]
                        result[person]["copies"] = 2
                    elif result[people[person]["father"]]["copies"] == 0 and result[people[person]["mother"]]["copies"] == 2:
                        result[person]["prob"] = PROBS['mutation'] * (1 - PROBS['mutation']) * PROBS["trait"][2][True]
                        result[person]["copies"] = 2
                    elif result[people[person]["father"]]["copies"] == 1 and result[people[person]["mother"]]["copies"] == 0:
                        result[person]["prob"] = PROBS['mutation'] * (0.5 - PROBS['mutation']) * PROBS["trait"][2][True]
                        result[person]["copies"] = 2
                    elif result[people[person]["father"]]["copies"] == 1 and result[people[person]["mother"]]["copies"] == 2:
                        result[person]["prob"] = (0.5 -PROBS['mutation']) * (1 - PROBS['mutation']) * PROBS["trait"][2][True]
                        result[person]["copies"] = 2
                    elif result[people[person]["father"]]["copies"] == 2 and result[people[person]["mother"]]["copies"] == 0:
                        result[person]["prob"] = PROBS['mutation'] * (1 - PROBS['mutation']) * PROBS["trait"][2][True]
                        result[person]["copies"] = 2
                    elif result[people[person]["father"]]["copies"] == 2 and result[people[person]["mother"]]["copies"] == 1:
                        result[person]["prob"] = (0.5 -PROBS['mutation']) * (1 - PROBS['mutation']) * PROBS["trait"][2][True]
                        result[person]["copies"] = 2
                        
                elif person not in two_genes and person not in one_gene and person in have_trait:
                    if result[people[person]["father"]]["copies"] == 0 and result[people[person]["mother"]]["copies"] == 0:
                        result[person]["prob"] = (1 - PROBS["mutation"]) * (1 - PROBS['mutation']) * PROBS["trait"][0][True]
                        result[person]["copies"] = 0
                    elif result[people[person]["father"]]["copies"] == 1 and result[people[person]["mother"]]["copies"] == 1:
                        result[person]["prob"] = (0.5 - PROBS['mutation']) * (0.5 - PROBS['mutation']) * PROBS["trait"][0][True]
                        result[person]["copies"] = 0
                    elif result[people[person]["father"]]["copies"] == 2 and result[people[person]["mother"]]["copies"] == 2:
                        result[person]["prob"] = PROBS["mutation"] * PROBS['mutation'] * PROBS["trait"][0][True]
                        result[person]["copies"] = 0
                    elif result[people[person]["father"]]["copies"] == 0 and result[people[person]["mother"]]["copies"] == 1:
                        result[person]["prob"] = (1 - PROBS['mutation']) * (0.5 - PROBS['mutation']) * PROBS["trait"][0][True]
                        result[person]["copies"] = 0
                    elif result[people[person]["father"]]["copies"] == 0 and result[people[person]["mother"]]["copies"] == 2:
                        result[person]["prob"] = (1 - PROBS['mutation']) * PROBS['mutation'] * PROBS["trait"][0][True]
                        result[person]["copies"] = 0
                    elif result[people[person]["father"]]["copies"] == 1 and result[people[person]["mother"]]["copies"] == 0:
                        result[person]["prob"] = (1 - PROBS['mutation']) * (0.5 - PROBS['mutation']) * PROBS["trait"][0][True]
                        result[person]["copies"] = 0
                    elif result[people[person]["father"]]["copies"] == 1 and result[people[person]["mother"]]["copies"] == 2:
                        result[person]["prob"] =  PROBS['mutation'] * (0.5 - PROBS['mutation']) * PROBS["trait"][0][True]
                        result[person]["copies"] = 0
                    elif result[people[person]["father"]]["copies"] == 2 and result[people[person]["mother"]]["copies"] == 0:
                        result[person]["prob"] = (1 - PROBS['mutation']) * PROBS['mutation'] * PROBS["trait"][0][True]
                        result[person]["copies"] = 0
                    elif result[people[person]["father"]]["copies"] == 2 and result[people[person]["mother"]]["copies"] == 1:
                        result[person]["prob"] = (0.5 - PROBS['mutation']) * PROBS['mutation'] * PROBS["trait"][0][True]
                        result[person]["copies"] = 0
            
            if result[person]["prob"] == 0:
                count += 1
                
    joint_prob = 1 
    
    for person in result:
        joint_prob = joint_prob * result[person]["prob"]
    
    #print("joint_prob:", joint_prob)
    #print("result:", result)
                
    return joint_prob
            

def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        if person in have_trait:
            probabilities[person]["trait"][True] += p 
        
        else:
            probabilities[person]["trait"][False] += p
    
    
    for person in probabilities:
        if person in one_gene:
            probabilities[person]["gene"][1] += p
        
        elif person in two_genes:
            probabilities[person]["gene"][2] += p
        else:
            probabilities[person]["gene"][0] += p
    
    return None 


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        
        sum_gene = 0 
        for number in probabilities[person]["gene"]:
            #print("sum_gene: ", sum_gene)
            sum_gene += probabilities[person]["gene"][number]
            
        for number in probabilities[person]["gene"]:
            probabilities[person]["gene"][number] = probabilities[person]["gene"][number] / sum_gene
        
        sum_trait = 0 

        sum_trait += probabilities[person]["trait"][True]
        sum_trait += probabilities[person]["trait"][False]
        
        #print("sum_trait: ", sum_trait)
        probabilities[person]["trait"][True] = probabilities[person]["trait"][True] / sum_gene
        probabilities[person]["trait"][False] = probabilities[person]["trait"][False] / sum_gene
            
    return None 


if __name__ == "__main__":
    main()
