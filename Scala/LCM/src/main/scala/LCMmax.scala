
import scala.collection.{Map, mutable}

object LCMmax {
  case class Item(item: Int, count: Int)

  var buckets: Map[Int, List[Transaction]] = Map.empty
  var closures: mutable.Queue[List[Int]] = new mutable.Queue[List[Int]]
  var closures2: mutable.HashMap[List[Int], Int] = new mutable.HashMap()
  var uniqueElements: List[Int] = List.empty[Int]

  def main(args: Array[String]): Unit = {

    val T: List[Transaction] = List(
      new Transaction(List(1, 2, 5, 7, 9)),
      new Transaction(List(1, 3, 5, 7, 9)),
      new Transaction(List(2, 4, 1, 3)),
      new Transaction(List(1, 3, 4, 5, 6)),
      new Transaction(List(1, 2)),
      new Transaction(List(2, 1)),
      new Transaction(List(1, 7, 2, 3, 4, 5, 8, 9)),
      new Transaction(List(6, 1, 2)),
      new Transaction(List(4, 5, 6)),
      new Transaction(List(8, 2, 5)),
      new Transaction(List(9, 2, 1)),
      new Transaction(List(1, 2, 4, 8, 9))
    )

    /*
    val T: List[Transaction] = List(
      new Transaction(List(1, 2, 5, 7, 9)),
      new Transaction(List(2, 4, 1, 3)),
      new Transaction(List(1, 3, 4, 5, 6)),
      new Transaction(List(1, 2)),
      new Transaction(List(2, 5, 8)),
      new Transaction(List(2, 1)),
      new Transaction(List(6, 1, 2)),
      new Transaction(List(4, 5, 6)),
      new Transaction(List(8, 2, 5)),
      new Transaction(List(9, 2, 1))
    )
    */
    /*
    val T: List[Transaction] = List(
      new Transaction(List(1,2,5,6,7,9)),
      new Transaction(List(2,3,4,5)),
      new Transaction(List(1,2,7,8,9)),
      new Transaction(List(1,7,9)),
      new Transaction(List(2,7,9)),
      new Transaction(List(2))
    )
    */
    uniqueElements = T.flatMap(_.items).distinct.sorted


    buckets = occurrenceDeliver(T)
    //buckets.map(b => s"${b._1} -> ${b._2}").foreach(println)

    val P = new Itemset(List.empty)
    backtracking(P, buckets)
  }


  def backtracking(P: Itemset, buckets: Map[Int, List[Transaction]]): Itemset = {
    //val I = buckets.map(b => Item(b._1, b._2.size)).toList.sortBy(i => i.count * -1).map(_.item)
    val I = buckets.map(b => Item(b._1, b._2.size)).toList.sortBy(i => i.item).map(_.item)//.filter(_ > P.tail())
    //println(s"P: $P => ${I.mkString(" ")}")

    if(I.nonEmpty){
      I.foreach{ e =>
        val P_prime = P.U(e)
        P_prime.count = buckets(e).size
        P_prime.setDenotation(buckets(e).toSet)

        //println(s"e: $e PUe: $P_prime} Clo(P): ${P.closure} Clo(PUe): ${P_prime.closure}")
        //println(s"The denotation of $P_prime is ${P_prime.denotation}")
        //println(s"The closure of $P_prime is ${P_prime.closure()}")

        //closures.enqueue(P_prime.closure)
/*
        closures2.get(P_prime.closure) match {
          case Some(_: Int) => //if(e_star < e) closures2.update(P_prime.closure, e_star )
          case None => closures2 += (P_prime.closure -> e)
        }
*/

        //println("Printing set of closures:")
        //closures2.foreach(println)

        //val j = closures2.getOrElse(P_prime.items, 0)
        /*
        var i = 0
        var j = 0
        while(i < closures.size){
          if(closures.get(i).get.equals(P_prime.items)){
            j = i + 1
            i = closures.size
          }
          i = i + 1
        }
        */
        //println(s"The closure tail for $P_prime($e) is $j")

        val isPPC = P.prefix(e).equals(P_prime.prefix(e)) && P_prime.items.equals(P_prime.closure)
        //println(s"Is $P_prime PPC? $isPPC")

        if(isPPC && P_prime.count == 1 /*e > j*/){
          println(P_prime)
        }

        val T_prime = buckets(e).map(t => new Transaction(t.items/*.filter(_ > e)*/))
        val I_prime = T_prime.flatMap(_.items.filter(_ > e)).distinct
        val buckets_prime = occurrenceDeliver(T_prime, I_prime)

        backtracking(P_prime, buckets_prime)

        //closures.dequeue()
        //closures2.filter(c => c._2 < e)
      }
    }

    P
  }

  def occurrenceDeliver(t_prime: List[Transaction], i_prime: List[Int]): scala.collection.Map[Int, List[Transaction]] = {
    var b_prime = new mutable.HashMap[Int, List[Transaction]]()
    for (t <- t_prime) {
      for (i <- i_prime) {
        if(t.contains(i) >= 0){
          b_prime.get(i) match {
            case Some(ts: List[Transaction]) => b_prime.update(i, ts :+ t)
            case None => b_prime += (i -> List(t))
          }
        }
      }
    }
    b_prime.mapValues(_.distinct)
  }

  def occurrenceDeliver(transactions: List[Transaction]): scala.collection.Map[Int, List[Transaction]] = {
    var buckets = new mutable.HashMap[Int, List[Transaction]]()
    for (transaction <- transactions) {
      for (element <- uniqueElements) {
        if(transaction.contains(element) >= 0){
          buckets.get(element) match {
            case Some(ts: List[Transaction]) => buckets.update(element, ts :+ transaction)
            case None => buckets += (element -> List(transaction))
          }
        }
      }
    }
    buckets.mapValues(_.distinct)
  }
}
