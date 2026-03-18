#include <iostream>
using namespace std;

class student{
    public:
    string name1 = "dhiraj";
    char name[50] = "dhiraj, hello my name is ";
};
int main() {
    student s;
    cout<<s.name1<<endl;
    student* v = new student();
    cout<<v->name1<<endl;
    int i = 0;
    while(s.name[i] != '\0'){
    cout<<s.name[i];
        i++;
    }

    return 0;
}