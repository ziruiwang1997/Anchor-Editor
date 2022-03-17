using Anchor_Editor_Backend.Models;
using System.Collections.Generic;
using System.Linq;
using System;
using System.Collections;

namespace Anchor_Editor_Backend.Repository
{
    public class AnchorRepository : IAnchorRepository
    {
        public IList<Anchor> AnchorList { get; set; }

        public Hashtable NestedAnchorsByLocation ()
        {
            Hashtable nestedAnchors = new Hashtable();

            foreach(Anchor anchor in AnchorList)
            {
                if (nestedAnchors[anchor.Location] == null)
                {
                    nestedAnchors[anchor.Location] = anchor.ToString();
                }
                else
                {
                    nestedAnchors[anchor.Location] += anchor.ToString();
                }
            }

            return nestedAnchors;
        }

        public Anchor GetAnchorByTimestamp(string timestamp)
        {
            Anchor anchor = AnchorList.Where(x => x.Timestamp == timestamp).FirstOrDefault();
            return anchor;
        }

        public IList<Anchor> GetAnchorByLocation(int location)
        {
            IList<Anchor> anchor = AnchorList.Where(x => x.Location == location).ToList();
            return anchor;
        }

        public void DeleteAnchorByTimestamp(string timestamp)
        {
            var anchorsToRemove = AnchorList.Where(x => x.Timestamp == timestamp).ToList();
            foreach (var anchor in anchorsToRemove)
                AnchorList.Remove(anchor);
        }

        public void AddAnchorByTimestamp(string timestamp, int location)
        {
            Anchor anchor = new Anchor(timestamp, location);    
            AnchorList.Add(anchor);
        }

        public void EditAnchor(string originalTimestamp, int originalLocation, string destinationTimestamp, int destinationLocation)
        {
            Anchor anchor = AnchorList.Where(x => x.Timestamp == originalTimestamp && x.Location == originalLocation).FirstOrDefault();
            anchor.Timestamp = destinationTimestamp;
            anchor.Location = destinationLocation;
        }
    }
}
