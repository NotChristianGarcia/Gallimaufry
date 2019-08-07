package main

import(
	"fmt"
	"time"
)

//func <func_name>(<parameters>) <return_type> {
//		content	
//}


// func type var
func test(x, y int) (int, int){
	return y, x
}

func main(){
	var x, y int = 9, 16
	z := 25

	fmt.Println("Hello World\n")
	fmt.Println("The time is ", time.Now())

	var n, m = test(x,y)
	var wowza float64 = float64(n)

	fmt.Println(n, m)
	fmt.Printf("Z (type): %T\tZ (value):%v\n", z, z)
	fmt.Println(wowza)
}