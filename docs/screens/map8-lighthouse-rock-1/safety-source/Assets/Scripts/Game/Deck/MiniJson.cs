using System.Collections.Generic;
using System.Globalization;
using System.Text;

namespace Catchline.Game.Deck
{
    // Minimal JSON reader for station files (JsonUtility cannot read nested arrays).
    // Objects become Dictionary<string, object>, arrays List<object>, numbers double.
    public static class MiniJson
    {
        public static object Parse(string text) { int i = 0; var v = Value(text, ref i); return v; }

        static void Space(string s, ref int i) { while (i < s.Length && char.IsWhiteSpace(s[i])) i++; }

        static object Value(string s, ref int i)
        {
            Space(s, ref i);
            if (i >= s.Length) throw new System.FormatException("Unexpected end of JSON");
            char c = s[i];
            if (c == '{') return Obj(s, ref i);
            if (c == '[') return Arr(s, ref i);
            if (c == '"') return Str(s, ref i);
            if (s.Length - i >= 4 && string.CompareOrdinal(s, i, "true", 0, 4) == 0) { i += 4; return true; }
            if (s.Length - i >= 5 && string.CompareOrdinal(s, i, "false", 0, 5) == 0) { i += 5; return false; }
            if (s.Length - i >= 4 && string.CompareOrdinal(s, i, "null", 0, 4) == 0) { i += 4; return null; }
            int start = i;
            while (i < s.Length && "+-0123456789.eE".IndexOf(s[i]) >= 0) i++;
            if (start == i) throw new System.FormatException($"Unexpected '{c}' at {i}");
            return double.Parse(s.Substring(start, i - start), CultureInfo.InvariantCulture);
        }

        static Dictionary<string, object> Obj(string s, ref int i)
        {
            var d = new Dictionary<string, object>(); i++;
            for (;;)
            {
                Space(s, ref i);
                if (s[i] == '}') { i++; return d; }
                string key = Str(s, ref i); Space(s, ref i);
                if (s[i] != ':') throw new System.FormatException($"Expected ':' at {i}");
                i++; d[key] = Value(s, ref i); Space(s, ref i);
                if (s[i] == ',') i++;
            }
        }

        static List<object> Arr(string s, ref int i)
        {
            var a = new List<object>(); i++;
            for (;;)
            {
                Space(s, ref i);
                if (s[i] == ']') { i++; return a; }
                a.Add(Value(s, ref i)); Space(s, ref i);
                if (s[i] == ',') i++;
            }
        }

        static string Str(string s, ref int i)
        {
            var b = new StringBuilder(); i++;
            while (s[i] != '"')
            {
                char c = s[i++];
                if (c != '\\') { b.Append(c); continue; }
                char e = s[i++];
                switch (e)
                {
                    case 'n': b.Append('\n'); break;
                    case 't': b.Append('\t'); break;
                    case 'r': b.Append('\r'); break;
                    case 'b': b.Append('\b'); break;
                    case 'f': b.Append('\f'); break;
                    case 'u': b.Append((char)int.Parse(s.Substring(i, 4), NumberStyles.HexNumber)); i += 4; break;
                    default: b.Append(e); break;
                }
            }
            i++; return b.ToString();
        }
    }
}
