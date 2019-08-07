// Class Implementation of BlockChain in Go (early)

package main

import(
	"fmt"
)

var (
	maxNonce uint64 = 1<<32
)

type BlockChain struct{
	blocks []Block
}

type Block struct{
	prevHash string
	transactions []Transaction // array/slice of transactions
	bits int8
	nonce uint64
}

type Transaction struct{
	receiver,sender string
	amount int
}

// returns nothing; prints values and plots
func testTime(N int, bits int){
	var times []int

	for i:=0; i<N; i++{
		times = append(times, i)
		fmt.Println(times)
	}
}

func main(){
	fmt.Println("Hello World")

	testTime(12, 8)

//	var genesisBlock = map[]		dictionary version that is not implemented


}