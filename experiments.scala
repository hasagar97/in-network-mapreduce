
import spark.implicits._ 	
import org.apache.spark.sql.types._
sc.setLogLevel("off")


def runExperiment(xx:Int) :(Int,Long,Long,Long) ={
	val file_name = "BigBoy_"+xx+".csv"
	// bag of words
	val text_file = sc.textFile(file_name)
	var t0 = System.currentTimeMillis()
	val counts = text_file.flatMap(line => line.split(" ")).map(word => (word, 1)).reduceByKey(_+_)
	counts.collect()
	var t1 = System.currentTimeMillis()
	print("Word_count :::"+(t1-t0)+"---"+xx)
	val wc_time = t1-t0
	// reading df
	val schema = new StructType()
	      .add("line_num",StringType,true)
	      .add("var_1",StringType,true)
	      .add("var_2",StringType,true)
	      .add("idd",IntegerType,true)

	val df = spark.read.format("csv")
	      .option("header", "true")
	      .schema(schema)
	      .load(file_name)

	// group by count
	t0 = System.currentTimeMillis()
	val df2 = df.groupBy("idd").count()
	df2.show(1,false)
	t1 = System.currentTimeMillis()
	print("Group_by :::"+(t1-t0)+"---"+xx)
	val gb_time = t1-t0

	// filter
	t0 = System.currentTimeMillis()
	df2.filter($"idd" <5).show(1,false)
	t1 = System.currentTimeMillis()

	print("Filter :::"+(t1-t0)+"---"+xx)
	val fil_time = t1-t0
	return (xx,wc_time,gb_time,fil_time)
}

var a : List[(Int,Long,Long,Long)] = List()
List(10,100,1000,10000,100000,1000000).foreach(x => a = a:+runExperiment(x))
a.toDF("Records","Word_count","groupBy","filter").show(100,false)







// val columns = Seq("language","users_count")
// val data = Seq(("Java", "20000"), ("Python", "100000"), ("Scala", "3000"))
// val rdd = spark.sparkContext.parallelize(data)


// def runPrimaryTest(): Unit = {
// 	val df = rdd.toDF("language","users_count")
// 	df.printSchema()
// 	val df2 = df.groupBy("language").count
// 	df2.show()
// }

// runPrimaryTest
