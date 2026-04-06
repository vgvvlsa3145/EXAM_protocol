from django.core.management.base import BaseCommand
from questions.models import Question, Option, Subject
from exams.models import Exam
from django.utils import timezone
from datetime import timedelta
import re

class Command(BaseCommand):
    help = 'Seeds Java Questions for Mock Test 1'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding Java Questions...")
        
        # 1. Subject
        subject_name = 'Java Mock'
        subject_code = 'JAVA_MOCK_001'
        try:
            subject = Subject.objects.get(code=subject_code)
        except Subject.DoesNotExist:
            subject = Subject.objects.create(name=subject_name, code=subject_code)
            
        # Clear existing questions for this subject to avoid duplicates on re-run
        Question.objects.filter(subject=subject).delete()
        
        # 2. Define Question Data
        # Theory Block 1 (1-40) + Block 2 (41-100)
        theory_raw = """
1. Java is a ______ language.
A) Low-level
B) Assembly
C) High-level
D) Machine
Answer: C

2. Java was developed by ______.
A) Microsoft
B) Sun Microsystems
C) Oracle
D) IBM
Answer: B

3. Java follows which principle?
A) Write many run many
B) Write once run anywhere
C) Compile once run once
D) Write anywhere run once
Answer: B

4. Java source file extension is:
A) .class
B) .exe
C) .java
D) .jar
Answer: C

5. Java bytecode file extension is:
A) .java
B) .exe
C) .class
D) .obj
Answer: C

6. Which component converts .java to .class?
A) JVM
B) JRE
C) JDK
D) Compiler (javac)
Answer: D

7. JVM stands for:
A) Java Variable Machine
B) Java Virtual Machine
C) Java Verified Machine
D) Java Visual Machine
Answer: B

8. Which memory stores objects?
A) Stack
B) Heap
C) Register
D) Cache
Answer: B

9. Which memory stores local variables?
A) Heap
B) Stack
C) Method area
D) ROM
Answer: B

10. Entry point of Java program is:
A) start()
B) run()
C) main()
D) init()
Answer: C

11. Correct main method signature is:
A) public void main()
B) static void main()
C) public static void main(String[] args)
D) void main(String args)
Answer: C

12. Which keyword makes method callable without object?
A) final
B) public
C) static
D) private
Answer: C

13. Which is NOT a primitive data type?
A) int
B) double
C) String
D) char
Answer: C

14. Size of int is:
A) 1 byte
B) 2 bytes
C) 4 bytes
D) 8 bytes
Answer: C

15. Which is used to store true/false?
A) int
B) char
C) boolean
D) byte
Answer: C

16. Which symbol is used for single character?
A) " "
B) ' '
C)
D) ( )
Answer: B

17. Which data type stores decimal values?
A) int
B) char
C) float
D) boolean
Answer: C

18. Default decimal data type is:
A) float
B) double
C) long
D) int
Answer: B

19. Which suffix is used for float?
A) d
B) l
C) f
D) s
Answer: C

20. Which keyword is used to take input?
A) input
B) Scanner
C) Read
D) System
Answer: B

21. Scanner class is present in:
A) java.lang
B) java.io
C) java.util
D) java.net
Answer: C

22. Which method reads integer input?
A) next()
B) nextLine()
C) nextInt()
D) nextChar()
Answer: C

23. Which operator gives remainder?
A) /
B) *
C) %
D) +
Answer: C

24. Output of 5 / 2 is:
A) 2.5
B) 3
C) 2
D) Error
Answer: C

25. Output of 5.0 / 2 is:
A) 2
B) 2.0
C) 2.5
D) Error
Answer: C

26. ++ is called:
A) Addition
B) Increment
C) Decrement
D) Assignment
Answer: B

27. Which operator compares values?
A) =
B) ==
C) +=
D) !=
Answer: B

28. Logical AND operator is:
A) &
B) &&
C) ||
D) !
Answer: B

29. Which statement checks multiple conditions?
A) if
B) if-else
C) else
D) else if
Answer: D

30. Which loop runs at least once?
A) for
B) while
C) do-while
D) foreach
Answer: C

31. Array index starts from:
A) 1
B) 0
C) -1
D) any number
Answer: B

32. Length of array is accessed by:
A) size()
B) count
C) length
D) length()
Answer: C

33. Which stores text?
A) char
B) int
C) String
D) boolean
Answer: C

34. Strings are:
A) Mutable
B) Immutable
C) Static
D) Final only
Answer: B

35. Correct way to compare strings:
A) ==
B) equals()
C) compare()
D) match()
Answer: B

36. Which method reverses StringBuilder?
A) change()
B) reverse()
C) swap()
D) back()
Answer: B

37. Which loop is best when count is known?
A) while
B) do-while
C) for
D) infinite
Answer: C

38. Which keyword stops loop?
A) stop
B) end
C) break
D) exit
Answer: C

39. Which skips current iteration?
A) skip
B) pass
C) continue
D) break
Answer: C

40. Java is:
A) Platform dependent
B) Platform independent
C) OS dependent
D) Machine dependent
Answer: B

41. Which keyword is used to create an object?
A) class
B) new
C) create
D) object
Answer: B

42. Which concept allows code reusability?
A) Abstraction
B) Encapsulation
C) Inheritance
D) Polymorphism
Answer: C

43. Which access modifier allows access only within the same class?
A) public
B) protected
C) default
D) private
Answer: D

44. Which keyword prevents inheritance?
A) static
B) final
C) private
D) protected
Answer: B

45. Which keyword refers to current object?
A) current
B) object
C) this
D) super
Answer: C

46. Constructor name must be same as:
A) method
B) variable
C) class
D) package
Answer: C

47. Constructor has:
A) return type
B) void return
C) no return type
D) int return
Answer: C

48. Which method is automatically called when object is created?
A) main
B) constructor
C) static block
D) finalize
Answer: B

49. Static members belong to:
A) Object
B) Heap
C) Class
D) Stack
Answer: C

50. Static variables are stored in:
A) Heap
B) Stack
C) Method Area
D) Register
Answer: C

51. Can static method access instance variables?
A) Yes
B) No
C) Sometimes
D) Only public
Answer: B

52. final variable means:
A) Can change later
B) Constant
C) Private
D) Static
Answer: B

53. Which keyword is used for inheritance?
A) implements
B) inherits
C) extends
D) super
Answer: C

54. Java supports:
A) Multiple inheritance (class)
B) Single inheritance
C) Hybrid inheritance
D) Circular inheritance
Answer: B

55. Which is parent class of all classes?
A) Main
B) Object
C) Class
D) System
Answer: B

56. Which keyword calls parent constructor?
A) this
B) super
C) parent
D) base
Answer: B

57. Method overriding happens in:
A) Same class
B) Different class
C) Parent class only
D) Child class only
Answer: B

58. Which keyword is used to prevent method overriding?
A) static
B) private
C) final
D) abstract
Answer: C

59. Which loop is best when condition is unknown?
A) for
B) while
C) do-while
D) foreach
Answer: B

60. Array size is:
A) Dynamic
B) Fixed
C) Unlimited
D) Optional
Answer: B

61. Which exception occurs when array index is wrong?
A) NullPointerException
B) NumberFormatException
C) ArrayIndexOutOfBoundsException
D) IOException
Answer: C

62. Which is mutable?
A) String
B) StringBuilder
C) Integer
D) Boolean
Answer: B

63. Which method compares string content?
A) ==
B) compare
C) equals()
D) match()
Answer: C

64. Which keyword is used to stop inheritance?
A) static
B) private
C) final
D) protected
Answer: C

65. JVM is part of:
A) JDK
B) JRE
C) OS
D) Compiler
Answer: B

66. JDK contains:
A) JVM only
B) JRE only
C) Compiler + JRE
D) Editor only
Answer: C

67. Which package is imported automatically?
A) java.util
B) java.io
C) java.lang
D) java.net
Answer: C

68. Which keyword handles exception?
A) throw
B) throws
C) try-catch
D) error
Answer: C

69. Which keyword is used to create thread?
A) start
B) run
C) Thread
D) Runnable
Answer: C

70. Which collection allows duplicates?
A) Set
B) Map
C) List
D) TreeSet
Answer: C

71. Which collection does NOT allow duplicates?
A) ArrayList
B) Vector
C) HashSet
D) LinkedList
Answer: C

72. Which collection maintains insertion order?
A) HashSet
B) TreeSet
C) LinkedHashMap
D) HashMap
Answer: C

73. Which is FIFO?
A) Stack
B) Queue
C) Vector
D) Set
Answer: B

74. Which is LIFO?
A) Queue
B) Array
C) Stack
D) List
Answer: C

75. Which method removes element from stack?
A) push()
B) add()
C) pop()
D) peek()
Answer: C

76. Which keyword is used to create interface?
A) class
B) interface
C) implements
D) extends
Answer: B

77. Interface methods are by default:
A) private
B) protected
C) public
D) static
Answer: C

78. Which keyword implements interface?
A) extends
B) interface
C) implements
D) inherit
Answer: C

79. Which statement ends program execution?
A) break
B) return
C) System.exit(0)
D) continue
Answer: C

80. Garbage collection works on:
A) Stack
B) Heap
C) Register
D) Method area
Answer: B

81. Which class is immutable?
A) String
B) StringBuilder
C) StringBuffer
D) ArrayList
Answer: A

82. Which operator checks object reference?
A) equals()
B) ==
C) instanceof
D) compareTo()
Answer: B

83. instanceof is used to:
A) Create object
B) Compare values
C) Check object type
D) Call constructor
Answer: C

84. Which loop is infinite?
A) for(;;)
B) while(false)
C) do-while(false)
D) none
Answer: A

85. Which method returns string length?
A) size()
B) count()
C) length()
D) getLength()
Answer: C

86. Which is checked exception?
A) ArithmeticException
B) NullPointerException
C) IOException
D) ArrayIndexOutOfBoundsException
Answer: C

87. Which keyword throws exception manually?
A) try
B) throw
C) throws
D) catch
Answer: B

88. Which keyword declares exception?
A) try
B) catch
C) throw
D) throws
Answer: D

89. Which statement executes first?
A) static block
B) main
C) constructor
D) instance block
Answer: A

90. Which operator has highest precedence?
A) +
B) *
C) ++
D) ==
Answer: C

91. Which loop is best for arrays?
A) while
B) for
C) do-while
D) goto
Answer: B

92. Which is NOT a loop?
A) for
B) while
C) repeat
D) do-while
Answer: C

93. Which keyword is optional in default access?
A) default
B) none
C) public
D) protected
Answer: B

94. Which method converts string to uppercase?
A) toUpper()
B) upper()
C) toUpperCase()
D) capitalize()
Answer: C

95. Which keyword stops current loop iteration?
A) break
B) stop
C) continue
D) exit
Answer: C

96. Which is correct file name?
A) hello.java
B) HelloWorld.class
C) HelloWorld.java
D) main.java
Answer: C

97. Which method starts thread?
A) run()
B) start()
C) execute()
D) begin()
Answer: B

98. Which keyword makes variable class-level?
A) final
B) public
C) static
D) private
Answer: C

99. Which keyword avoids NullPointerException?
A) null
B) Optional
C) try
D) static
Answer: B

100. Java is mainly used for:
A) Hardware design
B) Web & enterprise apps
C) OS kernel
D) Game engine only
Answer: B
"""

        # Program Blocks (1-10 + 11-50)
        program_raw = """
1.
int a = 5;
System.out.println(a++);

A) 6
B) 5
C) 4
D) Error
Answer: B

2.
int a = 5;
System.out.println(++a);

A) 5
B) 4
C) 6
D) Error
Answer: C

3.
System.out.println(10 + 5 * 2);

A) 30
B) 20
C) 25
D) 15
Answer: B

4.
System.out.println(10 % 3);

A) 3
B) 1
C) 0
D) 10
Answer: B

5.
for(int i=1;i<=3;i++)
 System.out.print(i);

A) 1 2 3
B) 123
C) 012
D) Error
Answer: B

6.
int[] a = {10,20,30};
System.out.println(a[1]);

A) 10
B) 20
C) 30
D) Error
Answer: B

7.
String s = "Java";
System.out.println(s.length());

A) 3
B) 4
C) 5
D) Error
Answer: B

8.
System.out.println(5/2);

A) 2
B) 2.5
C) 3
D) Error
Answer: A

9.
int i=1;
while(i<=3){
 System.out.print(i);
 i++;
}

A) 123
B) 012
C) 321
D) Error
Answer: A

10.
System.out.println("Java".equals("java"));

A) true
B) false
C) Error
D) 0
Answer: B

11.
int a = 10;
a += 5;
System.out.println(a);

A) 10
B) 15
C) 5
D) Error
Answer: B

12.
System.out.println(10 > 5 && 5 > 3);

A) true
B) false
C) Error
D) 0
Answer: A

13.
int a = 5;
int b = 10;
System.out.println(a > b ? a : b);

A) 5
B) 10
C) true
D) false
Answer: B

14.
int i = 1;
do {
 System.out.print(i);
 i++;
} while(i<=3);

A) 123
B) 012
C) 321
D) Error
Answer: A

15.
int[] a = {1,2,3,4};
System.out.println(a.length);

A) 3
B) 4
C) 5
D) Error
Answer: B

16.
String s1 = "Java";
String s2 = "Java";
System.out.println(s1 == s2);

A) true
B) false
C) Error
D) 0
Answer: A

17.
String s1 = new String("Java");
String s2 = new String("Java");
System.out.println(s1 == s2);

A) true
B) false
C) Error
D) 0
Answer: B

18.
System.out.println("Hello".substring(1,4));

A) Hel
B) ell
C) ello
D) error
Answer: B

19.
for(int i=5;i>0;i--){
 System.out.print(i);
}

A) 54321
B) 12345
C) 5432
D) Error
Answer: A

20.
int sum = 0;
for(int i=1;i<=5;i++)
 sum += i;
System.out.println(sum);

A) 10
B) 15
C) 20
D) 5
Answer: B

21.
System.out.println( (int)5.9 );

A) 6
B) 5
C) 5.9
D) Error
Answer: B

22.
int a = 0;
while(a<3){
 System.out.print(a);
 a++;
}

A) 012
B) 123
C) 321
D) Error
Answer: A

23.
System.out.println(10 == 10 || 5 > 10);

A) true
B) false
C) Error
D) 0
Answer: A

24.
StringBuilder sb = new StringBuilder("abc");
sb.reverse();
System.out.println(sb);

A) abc
B) cba
C) bac
D) Error
Answer: B

25.
int a = 5;
System.out.println(--a);

A) 5
B) 4
C) 6
D) Error
Answer: B

26.
int a = 10;
int b = 20;
System.out.println(a > b ? "A" : "B");

A) A
B) B
C) true
D) false
Answer: B

27.
for(int i=1;i<=3;i++){
 for(int j=1;j<=2;j++){
  System.out.print(j);
 }
}

A) 1212
B) 1122
C) 123
D) Error
Answer: A

28.
int i = 5;
while(i > 0){
 System.out.print(i);
 i--;
}

A) 12345
B) 54321
C) 4321
D) Error
Answer: B

29.
System.out.println(10 != 5);

A) true
B) false
C) 0
D) Error
Answer: A

30.
int[] a = {2,4,6};
for(int x : a){
 System.out.print(x);
}

A) 246
B) 2 4 6
C) 012
D) Error
Answer: A

31.
String s = "JAVA";
System.out.println(s.toLowerCase());

A) JAVA
B) java
C) Java
D) Error
Answer: B

32.
int x = 10;
if(x > 5)
 System.out.println("Yes");
else
 System.out.println("No");

A) Yes
B) No
C) Error
D) Nothing
Answer: A

33.
int i = 1;
do{
 System.out.print(i);
 i++;
}while(i<1);

A) 1
B) 0
C) Error
D) No output
Answer: A

34.
System.out.println(5 + "" + 10);

A) 15
B) 510
C) Error
D) 5 10
Answer: B

35.
int a = 3;
System.out.println(a*a);

A) 6
B) 9
C) 3
D) Error
Answer: B

36.
String s = "Hello";
System.out.println(s.charAt(1));

A) H
B) e
C) l
D) o
Answer: B

37.
int a = 5;
System.out.println(a++ + ++a);

A) 11
B) 12
C) 13
D) Error
Answer: C

38.
int[] a = new int[3];
System.out.println(a[0]);

A) 1
B) 0
C) Garbage value
D) Error
Answer: B

39.
System.out.println(Math.max(10,20));

A) 10
B) 20
C) Error
D) 0
Answer: B

40.
String s1 = "Hi";
String s2 = s1;
System.out.println(s1 == s2);

A) true
B) false
C) Error
D) 0
Answer: A

41.
int a = 10;
if(a % 2 == 0)
 System.out.println("Even");
else
 System.out.println("Odd");

A) Odd
B) Even
C) Error
D) Nothing
Answer: B

42.
int i;
for(i=0;i<3;i++);
System.out.print(i);

A) 3
B) 012
C) Infinite loop
D) Error
Answer: A

43.
static {
 System.out.print("A");
}
public static void main(String[] args){
 System.out.print("B");
}

A) AB
B) BA
C) B
D) Error
Answer: A

44.
class Test{
 Test(){
  System.out.print("C");
 }
 public static void main(String[] args){
  Test t = new Test();
 }
}

A) C
B) Test
C) Error
D) No output
Answer: A

45.
System.out.println(10/0);

A) 0
B) Infinity
C) Runtime error
D) Compile error
Answer: C

46.
int a = 5;
System.out.println(a > 10 && a++ > 4);
System.out.println(a);

A) false 6
B) false 5
C) true 6
D) true 5
Answer: B

47.
int a = 5;
System.out.println(a < 10 || a++ > 5);
System.out.println(a);

A) true 6
B) true 5
C) false 6
D) false 5
Answer: B

48.
String s = "Java";
s.concat("World");
System.out.println(s);

A) JavaWorld
B) World
C) Java
D) Error
Answer: C

49.
StringBuilder sb = new StringBuilder("Hi");
sb.append("Bye");
System.out.println(sb);

A) Hi
B) Bye
C) HiBye
D) Error
Answer: C

50.
int count = 0;
for(int i=1;i<=5;i++){
 if(i%2==0)
  count++;
}
System.out.println(count);

A) 1
B) 2
C) 3
D) 5
Answer: B
"""
        
        # 3. Import Logic Helper
        def import_qs(text, category):
             # Regex to find questions
             # Pattern: Number. (Any text) A) (Text) B) ... Answer: (X)
             # Note: Some questions have newlines in the question text.
             
             # Split by "^\d+\." (start of line)
             blocks = re.split(r'^\d+\.', text, flags=re.MULTILINE)[1:] # Skip empty first
             
             count = 0
             for block in blocks:
                 lines = block.strip().split('\n')
                 
                 # Extract Answer (last non-empty line)
                 # Find "Answer: X"
                 ans_line = None
                 for i in range(len(lines)-1, -1, -1):
                     if "Answer:" in lines[i]:
                         ans_line = lines[i]
                         lines.pop(i) # Remove it
                         break
                 
                 if not ans_line:
                     self.stdout.write(self.style.WARNING(f"Skipping block (no answer): {block[:20]}"))
                     continue
                 
                 correct_char = ans_line.split("Answer:")[1].strip().upper()  # 'A', 'B', 'C', 'D'
                 
                 # Extract Options (A), B), C), D))
                 options = {'A': '', 'B': '', 'C': '', 'D': ''}
                 q_text_lines = []
                 current_opt = None
                 
                 for line in lines:
                     line = line.strip()
                     if not line: continue
                     
                     if line.startswith('A)'):
                         current_opt = 'A'
                         options['A'] = line[2:].strip()
                     elif line.startswith('B)'):
                         current_opt = 'B'
                         options['B'] = line[2:].strip()
                     elif line.startswith('C)'):
                         current_opt = 'C'
                         options['C'] = line[2:].strip()
                     elif line.startswith('D)'):
                         current_opt = 'D'
                         options['D'] = line[2:].strip()
                     else:
                         if current_opt:
                             # Continuation of option? Or ignoring?
                             options[current_opt] += " " + line
                         else:
                             q_text_lines.append(line)
                 
                 q_text = "\n".join(q_text_lines).strip()
                 
                 if not q_text or not options['A']: 
                     continue
                     
                 # Create Question
                 question = Question.objects.create(
                     subject=subject,
                     text=q_text,
                     question_type='MCQ',
                     marks=1,
                     category=category,
                     difficulty='MEDIUM'
                 )
                 
                 # Create Options
                 for key in ['A', 'B', 'C', 'D']:
                     if options[key]:
                         Option.objects.create(
                             question=question,
                             text=options[key],
                             is_correct=(key == correct_char)
                         )
                 count += 1
             return count

        self.stdout.write("Importing Theory Questions...")
        t_count = import_qs(theory_raw, 'Theory')
        
        self.stdout.write("Importing Program Questions...")
        p_count = import_qs(program_raw, 'Program')
        
        self.stdout.write(self.style.SUCCESS(f"Imported {t_count} Theory and {p_count} Program questions."))
        
        # 4. Create Exam
        exam_title = "Mock test 1"
        start_time = timezone.now()
        end_time = start_time + timedelta(days=5) # Valid for 5 days
        
        exam, created = Exam.objects.get_or_create(
            title=exam_title,
            defaults={
                'subject': subject,
                'start_time': start_time,
                'end_time': end_time,
                'duration_minutes': 105, # 1 hr 45 mins
                'total_marks': 50, # Max score possible
                'warning_threshold': 10,
                'is_active': True,
                'random_question_count': 50
            }
        )
        
        # Link ALL questions
        all_qs = Question.objects.filter(subject=subject) # Assuming these are the ones we just added
        exam.questions.set(all_qs)
        exam.save()
        
        self.stdout.write(self.style.SUCCESS(f"Exam '{exam_title}' created/updated with {all_qs.count()} questions in the pool."))
