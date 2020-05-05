import user_test

test_files = [
    user_test
]

def main():
    print('-----------------------')
    print('| Starting all tests: |')
    print('----------------------- \n')

    for test in test_files:
        test.main()
        print('\n')

    print('-----------------------')
    print('|   Tests finished.   |')
    print('-----------------------')

if __name__ == '__main__':
    main()
