﻿namespace Anchor_Editor_Backend.Models
{
    public class Anchor
    {
        public string Timestamp { get; set; }
        public int Location { get; set; }

        public Anchor(string timestamp, int location)
        {
            Timestamp = timestamp;
            Location = location;
        }
    }
}
