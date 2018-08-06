
import scala.collection.{Map, mutable}

object LCMmax2 {
  case class Item(item: Int, count: Int)

  var buckets: Map[Int, List[Transaction]] = Map.empty
  var closures: mutable.Queue[List[Int]] = new mutable.Queue[List[Int]]
  var uniqueElements: List[Int] = List.empty[Int]

  def main(args: Array[String]): Unit = {
    /*
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
    */
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
    val T: List[Transaction] = List(
      new Transaction(List(1,2,5,6,7,9)),
      new Transaction(List(2,3,4,5)),
      new Transaction(List(1,2,7,8,9)),
      new Transaction(List(1,7,9)),
      new Transaction(List(2,7,9)),
      new Transaction(List(2))
    )

    uniqueElements = T.flatMap(_.items).distinct.sorted


    buckets = occurrenceDeliver(T)
    //buckets.map(b => s"${b._1} -> ${b._2}").foreach(println)

    val P = new Itemset(List.empty)
    LCMmax(P, buckets)
  }

  def LCMmax(P: Itemset, buckets: Map[Int, List[Transaction]]): Unit = {
    val I = buckets.keys.toList.sorted

    if(I.isEmpty){
      println(P)
    }

    I.foreach{ e =>
      val P_prime = P.U(e)
      P_prime.count = buckets(e).size
      P_prime.setDenotation(buckets(e).toSet)

      val cloP = new Itemset(P.items ++ P_prime.closure)
      val cloT = P_prime.denotationMinusClosure()
      val cloI = cloT.flatMap(_.items).distinct.sorted
      val cloBuckets = occurrenceDeliver(cloT, cloI)
      LCMmax(cloP, cloBuckets)
    }
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
