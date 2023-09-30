# zip 함수에 대해 알아보자.
print()
list1 = [1, 2, 3]
list2 = ['a', 'b']
zipped = zip(list1, list2)
print(zipped)
print(list(zipped))

print()
for i, j in [(1, 'a'), (2, 'b'), (3, 'c')]:
    print(i, j)

print()
print(*[1, 'a', 3, 4, 'n'])
# * 연산자: 이 연산자는 "splat" 또는 "unpacking" 연산자라고도 불립니다. 이 연산자를 사용하면 컬렉션의 원소들을 개별적으로 전개(unpack)할 수 있습니다. 

# zip은 Python의 내장 함수로, 여러 개의 iterable(예: 리스트, 튜플 등)을 입력 받아서 각 iterable의 원소들을 튜플로 묶어주는 역할을 합니다. 
# 결과적으로, 이 함수는 이터러블들의 원소들을 순서대로 튜플로 묶은 새로운 이터러블을 반환합니다.