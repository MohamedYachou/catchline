using UnityEngine;

namespace Catchline.Prototype
{
    // Tells a tap what it hit: a worker, a station or the deck floor.
    public class Clickable : MonoBehaviour
    {
        public Worker Worker;
        public Station Station;
        public bool Deck;
    }
}
