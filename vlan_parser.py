#!/usr/bin/env python

import unittest

class FilterModule(object):
    def filters(self):
        filter_dict = {
            'vlan_parser': self.vlan_parser
            }

        return filter_dict

    @staticmethod
    def vlan_parser(vlan_list):
        '''
            Input: Unsorted list of vlan integers
            Output: Sorted list of integers according to Cisco IOS vlan list rules

            1. Vlans are listed in ascending order
            2. Runs of 3 or more consecutive vlans are listed with a dash
            3. The first line of the list can be 48 characters long
            4. Subsequents list line can be 44 characters

            Example 1:
            interface GigabitEthernet1/36
             description EXAMPLE_1
             switchport trunk encapsulation dot1q
             switchport trunk allowed vlan 100,1688,3002-3005,3102-3105,3802,3900,3998,3999
             switchport mode trunk

            Example 2:
            interface GigabitEthernet1/37
             description EXAMPLE_2
             switchport trunk encapsulation dot1q
             switchport trunk allowed vlan 100,1688,3002,3004,3005,3050,3102,3104,3105,3151
             switchport trunk allowed vlan add 3802,3900,3998,3999
             switchport mode trunk
        '''

        #Sort and remove duplicates
        sorted_list = sorted(set(vlan_list))

        parse_list = []
        idx = 0
        while idx < len(sorted_list):
            start = idx
            end = start
            while end < len(sorted_list) - 1:
                if sorted_list[end + 1] - sorted_list[end] == 1:
                    end += 1
                else:
                    break

            if start == end:
                # Single VLAN
                parse_list.append(str(sorted_list[idx]))
            elif start + 1 == end:
                # Run of 2 VLANs
                parse_list.append(str(sorted_list[start]))
                parse_list.append(str(sorted_list[end]))
            else:
                # Run of 3 or more VLANs
                parse_list.append(str(sorted_list[start]) + '-' + str(sorted_list[end]))
            idx = end + 1

        line_count = 0
        result = ['']
        for vlans in parse_list:
            #First line (" switchport trunk allowed vlan ")
            if line_count == 0:
                if len(result[line_count] + vlans) > 48:
                    result.append('')
                    line_count += 1
                    result[line_count] += vlans + ','
                else:
                    result[line_count] += vlans + ','

            #Subsequent lines (" switchport trunk allowed vlan add ")
            else:
                if len(result[line_count] + vlans) > 44:
                    result.append('')
                    line_count += 1
                    result[line_count] += vlans + ','
                else:
                    result[line_count] += vlans + ','

        #Remove trailing orphan commas
        for idx in range(0, len(result)):
            result[idx] = result[idx].rstrip(',')

        #Sometimes text wraps to next line, but there are no remaining VLANs
        if '' in result:
            result.remove('')

        return result

class VLANParserMethods(unittest.TestCase):
    '''
        Example1: Sorted single line with compression
        Example2: Sorted multiple line, no compression
        Example3: Unsorted duplicates, single line with compression
    '''

    line1 = ' switchport trunk allowed vlan '
    line2 = ' switchport trunk allowed vlan add '
    ex1 = [100, 1688, 3002, 3003, 3004, 3005, 3102, 3103, 3104, 3105, 3802, 3900, 3998, 3999]
    ex2 = [100, 1688, 3002, 3004, 3005, 3050, 3102, 3104, 3105, 3151, 3802, 3900, 3998, 3999]
    ex3 = [3, 2, 1, 1, 2, 3, 1, 2, 3]

    def test_example1(self):
        '''
             switchport trunk allowed vlan 100,1688,3002-3005,3102-3105,3802,3900,3998,3999
        '''

        #Check number of lines in result
        self.assertTrue(len(FilterModule.vlan_parser(self.ex1)) == 1)

        #Verify VLAN list isn't too long
        self.assertTrue(len(FilterModule.vlan_parser(self.ex1)[0]) <= 48)
        for i in range(1, len(FilterModule.vlan_parser(self.ex1))):
            self.assertTrue(len(FilterModule.vlan_parser(self.ex1)[i]) <= 44)

        #Verify entire command doesn't exceed 80 chars
        self.assertTrue(len(self.line1 + FilterModule.vlan_parser(self.ex1)[0]) <= 80)
        for i in range(1, len(FilterModule.vlan_parser(self.ex1))):
            self.assertTrue(len(self.line2 + FilterModule.vlan_parser(self.ex1)[i]) <= 80)

        #Validate parsing rules
        self.assertTrue(FilterModule.vlan_parser(self.ex1)
                        == ['100,1688,3002-3005,3102-3105,3802,3900,3998,3999'])

    def test_example2(self):
        '''
             switchport trunk allowed vlan 100,1688,3002,3004,3005,3050,3102,3104,3105,3151
             switchport trunk allowed vlan add 3802,3900,3998,3999
        '''

        #Check number of lines in result
        self.assertTrue(len(FilterModule.vlan_parser(self.ex2)) == 2)

        #Verify VLAN list isn't too long
        self.assertTrue(len(FilterModule.vlan_parser(self.ex2)[0]) <= 48)
        for i in range(1, len(FilterModule.vlan_parser(self.ex2))):
            self.assertTrue(len(FilterModule.vlan_parser(self.ex2)[i]) <= 44)

        #Verify entire command doesn't exceed 80 chars
        self.assertTrue(len(self.line1 + FilterModule.vlan_parser(self.ex2)[0]) <= 80)
        for i in range(1, len(FilterModule.vlan_parser(self.ex2))):
            self.assertTrue(len(self.line2 + FilterModule.vlan_parser(self.ex2)[i]) <= 80)

        #Validate parsing rules
        self.assertTrue(FilterModule.vlan_parser(self.ex2)
                        == ['100,1688,3002,3004,3005,3050,3102,3104,3105,3151',
                            '3802,3900,3998,3999'])

    def test_example3(self):
        '''
             switchport trunk allowed vlan 1,2,3
        '''

        #Check number of lines in result
        self.assertTrue(len(FilterModule.vlan_parser(self.ex3)) == 1)

        #Verify VLAN list isn't too long
        self.assertTrue(len(FilterModule.vlan_parser(self.ex3)[0]) <= 48)
        for i in range(1, len(FilterModule.vlan_parser(self.ex3))):
            self.assertTrue(len(FilterModule.vlan_parser(self.ex3)[i]) <= 44)

        #Verify entire command doesn't exceed 80 chars
        self.assertTrue(len(self.line1 + FilterModule.vlan_parser(self.ex3)[0]) <= 80)
        for i in range(1, len(FilterModule.vlan_parser(self.ex3))):
            self.assertTrue(len(self.line2 + FilterModule.vlan_parser(self.ex3)[i]) <= 80)

        #Validate parsing rules
        self.assertTrue(FilterModule.vlan_parser(self.ex3) == ['1-3'])

if __name__ == '__main__':
    unittest.main()
