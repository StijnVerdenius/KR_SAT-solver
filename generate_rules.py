
import itertools




order = 3

expected_rule_count = 4 * order ** 4 * (1 + 4 * order ** 2)
print("Expected number of rules without duplicate removal:", expected_rule_count)

rules = set()

def generate_literal(x,y,pos):
    return int(str(x)+str(y)+str(pos))

def generate_existential_rules(_1, _2, order):
    exis_position = []
    exis_colum = []
    exis_row = []
    exis_sq = []

    # generate literals for a cell
    for _3 in range(1, order ** 2 + 1):
        exis_position.append(generate_literal(_1, _2, _3))
        exis_colum.append(generate_literal(_1, _3, _2))
        exis_row.append(generate_literal(_3, _1, _2))

    # if start of square, add that too
    if _1 % order == 1 and _2 % order == 1:

        for pos in range(1, order ** 2 + 1):
            loose = []
            for x in range(order):
                for y in range(order):
                    loose.append(generate_literal(_1+x, _2+y, pos))
            exis_sq.append(loose)

    print(exis_sq)

    return [exis_position, exis_colum, exis_row] + exis_sq

def generate_exclusion_rules(existential_rule):
    output = []


    for comb in itertools.permutations(existential_rule, 2):
        a = comb[0]
        b = comb[1]
        if (a > b):
            rule = (-b, -a)
        elif(b > a):
            rule = (-a, -b)
        else:
            raise Exception("a == b in itertools")

        output.append(rule)

    return output

duplicate_counter = 0
counter = 0
for _1 in range(1, order ** 2 + 1):
    for _2 in range(1, order ** 2 + 1):

        additional_rules = generate_existential_rules(_1, _2, order)

        for rule in additional_rules:
            # print(rule)
            rules.add(tuple(rule))
            counter += 1
            generated = generate_exclusion_rules(rule)

            counter = 0
            for rule_ in generated:
                before = len(rules)
                rules.add(tuple(rule_))
                if (len(rules) > before):
                    # print(rule_)
                    counter += 1
                else:
                    duplicate_counter += 1

print("Found and removed duplicate, remaining rule count:", len(rules))
