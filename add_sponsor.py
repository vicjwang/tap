import argparse
import sys
from bs4 import BeautifulSoup as bsoup

sponsor_file = "sponsors.txt"
out_file = "new_sponsors.txt"

def parse_sponsor_file(sponsor_file):
    '''
    returns [ (logo, company, blurb), ... ]
    '''
    with open(sponsor_file, 'r') as f:
        read_data = f.read()
    names = []
    images = []
    companies = []
    blurbs = []
    blurb = []
    is_blurb = False
    for line in read_data.split("\n"):
        if "[one_third]" in line or "[one_third_last]" in line:
            is_blurb = True
            continue
        elif "[/one_third]" in line or "[/one_third_last]" in line:
            is_blurb = False
            continue

        if "<h4>" in line:
            images.append(line)
        elif "<strong>" in line:
            name = bsoup(line).text
            names.append(name)
            companies.append(line)
        else: 
            if is_blurb:
                blurb.append(line)
            elif blurb:
                blurbs.append( " ".join(blurb) )
                blurb = []
    print "names",len(names)
    print "images",len(images)
    print "copanies",len(companies)
    print "blurbs",len(blurbs)
    return zip(names, images, companies, blurbs)

def format_and_write(lines):
    # wrap in [one_third], every last third gets [one_third_last]
    with open(out_file, 'w') as f:
        for i, line in enumerate(lines):
            name, img, com, blurb = line
            if i % 3 == 2:
                header = "[one_third_last]"
                footer = '[/one_third_last]\n\n[bra_divider Height="40"]\n'
            else:
                header = "[one_third]"
                footer = "[/one_third]"
    
            f.write("\n".join([header, img, com, blurb, footer, "\n"]))


def add_new_sponsor(lines, company, blurb):
    lines.append((company, "FILL IMAGE HERE", '<a href="FILL ME IN" target="_blank"><strong>{0}</strong></a>'.format(company), blurb))
    lines.sort(key= lambda x: x[0])
    return lines

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("company", help="<company>")
    parser.add_argument("blurb", help="<blurb>")
    args = parser.parse_args()
    
    company = args.company
    blurb = args.blurb
    
    lines = parse_sponsor_file(sponsor_file)
    lines = add_new_sponsor(lines, company, blurb)
    format_and_write(lines)

