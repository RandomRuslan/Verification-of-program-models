import sys

from tree_parser import parse_tokens

def main():
    output = 'out'
    input = '../in.txt'
    verbose = False

    asts = []
    funcs = []
    ast = parse_tokens(input)
    print(ast.my_print(ast))
    ast.export(output_path='../', name='out', detailed=verbose)
    asts += [ast]
    funcs_flow = {}
    for ast in asts:
        funcs = ast.children
        for i, func in enumerate(funcs):
            if func in funcs_flow:
                print('Same functions in one file. This is UNACCEPTABLE!... For now')
                sys.exit(2)

if __name__ == "__main__":
    main()
