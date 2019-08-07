package main

import "golang.org/x/tour/pic"

func Pic(dx, dy int) [][]uint8 {
	var picture [][]uint8

	for i:=0; i<dy; i++{
		var row []uint8
		for j:=0; j<dx; j++{
			row = append(row, uint8(i*j))
		}
		picture = append(picture, row)
	}
	
	return picture

}

func main() {
	pic.Show(Pic)
}