class AnimalFactory:
    def __init__(self):
        self._animal_types = {
            "dog": Dog,
            "cat": Cat,
            "rabbit": Rabbit
        }

    def __call__(self, type, age):
        return self._animal_types[type](age)

class Animal:
    def __init__(self, age):
        self._age = age

class Dog(Animal):
    def __init__(self, age):
        super().__init__(age)

class Cat(Animal):
    def __init__(self, age):
        super().__init__(age)

class Rabbit(Animal):
    def __init__(self, age):
        super().__init__(age)

animals_info = [{"type": "dog", "age": 2}, {"type": "cat", "age": 5}, {"type": "rabbit", "age": 3}]
animal_objects = []
create_animal = AnimalFactory()

for animal in animals_info:
    tmp = create_animal(animal["type"], animal["age"])
    animal_objects.append(tmp)

for animal in animal_objects:
    print(animal._age)