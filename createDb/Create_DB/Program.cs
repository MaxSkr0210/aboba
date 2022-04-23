using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using MongoDB.Bson;
using MongoDB.Driver;
using System.Linq;

namespace Parser
{
    internal class Program
    {
        private static readonly string PathToDesktopDirectory = Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory) + "\\";

        private static Dictionary<string, string> LatinWords = new Dictionary<string, string>()
        {
            { "прил", "nomen adjectivum" },
            { "сущ", "nomen substantivum" },
            { "гл", "verbum" },
            { "кр_прил", "nomen adjectivum" },
            { "деепр", "participium" },
            { "прич", "participium" },
            { "инф_гл", "verbum" },
            { "кр_прич", "participium" },
            { "предик", "Савин" },
            { "нареч", "adverbium" },
            { "комп", "Савин" },
            { "част", "particula" },
            { "межд", "interjectio" },
            { "числ", "nomen numerale" },
            { "предл", "praepositio" }
        };

        private static List<string> GetWordsFromFile(string fileName)
        {
            List<string> words = new List<string>();

            foreach (var str in File.ReadLines(PathToDesktopDirectory + fileName))
            {
                string tmpString = "";
                foreach (var sym in str)
                {
                    if (sym == ',' || sym == ' ')
                    {
                        break;
                    }
                    tmpString += sym;
                }
                words.Add(tmpString);
            }

            return words;
        }

        private static List<string> GetTranslate(string fileName)
        {
            List<string> translate = new List<string>();
            Stack<char> tmpStack = new Stack<char>();

            foreach (var str in File.ReadLines(PathToDesktopDirectory + fileName))
            {
                for (int i = str.Length - 1; i > 0; i--)
                {
                    if (str[i] == ' ' || str[i] == ',')
                        break;
                    else
                        tmpStack.Push(str[i]);
                }
                translate.Add(new string(tmpStack.ToArray()));
                tmpStack.Clear();
            }

            return translate;
        }

        static void Main()
        {

            MongoClient client = new MongoClient("mongodb+srv://Aboba:aboba777@cluster0.ts9bv.mongodb.net/myFirstDatabase?retryWrites=true&w=majority");

            var collection = client.GetDatabase("dictionary");
            var latin = collection.GetCollection<BsonDocument>("latinTest");

            List<string> translate = GetTranslate("bd.txt");
            List<string> words = GetWordsFromFile("bd.txt");

            DeepMorphy.MorphAnalyzer morph = new DeepMorphy.MorphAnalyzer();
            var results = morph.Parse(translate).ToArray();

            List<string> result = new List<string>();
            foreach (var item in results)
            {
                result.Add(item["чр"].BestGramKey.ToString());
            }

            if (words.Count != translate.Count)
                throw new Exception($"Word count: {words.Count} and Translate count: {translate.Count}");

            int count = 0;
            foreach (var word in words)
            {
                var doc = new BsonDocument()
                {
                    { "word", word},
                    { "translate", translate[count] },
                    {"type",  LatinWords[result[count]]}
                };

                latin.InsertOne(doc);
                count++;
            }

        }
    }
}
