# Password for my application

import random

lower_case = "abcdefghijklmnopqrstuvwxy"
upper_case = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
symbols = "~!@#$%^&*()_+-[];',./{}:<>?"
numbers_i = "1234567890"

use_for = lower_case + upper_case + symbols + numbers_i
lenght_for = 10

password = "".join(random.sample(use_for, lenght_for))

print("Your password is: ", password)


