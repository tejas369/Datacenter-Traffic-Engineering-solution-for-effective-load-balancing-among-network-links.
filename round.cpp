#include<iostream>
#include<algorithm>
#include<vector>
#include<iomanip>

using namespace std;

int main()
{
	double **topo1, **topo2;
	int spine, leaf;
	cout << " \nEnter number of spine and leaf : ";
	cin >> spine >> leaf;
	cout << endl;

	int flag = 0;
	cout << " \n press '1' for Uniform link capacity OR press 2 for reduced link capacity  : ";
	cin >> flag;

	//2D array initialization

	topo1 = new double*[spine];
	for (int r = 0; r < spine; r++)
		topo1[r] = new double[leaf];

	topo2 = new double*[spine];
	for (int r = 0; r < spine; r++)
		topo2[r] = new double[leaf];



	for (int row1 = 0; row1 < spine; row1++)
	{
		for (int col1 = 0; col1 < leaf; col1++)
			topo1[row1][col1] = 0;
	}

	for (int row2 = 0; row2 < spine; row2++)
	{
		for (int col2 = 0; col2 < leaf; col2++)
			topo2[row2][col2] = 0;
	}

	//No. of flows

	double f;
	cout << " \n\nEnter the value of f : ";
	cin >> f;
	double NOF;
	NOF = f*spine*leaf;
	cout << NOF << endl;
	int l1[1000], l2[1000];
	int a[1000];
	srand(time(NULL));
	
	//Algorithm starts

	for (int i = 0; i < NOF; i++)
	{


		l1[i] = rand() % leaf;
		l2[i] = rand() % leaf;
		while (l2[i] == l1[i])
		{
			l2[i] = rand() % leaf;
		}
		

	}
	
	int key[1000] = {0};
	for (int k = 0; k < leaf; k++)
	{
		for (int m = 0; m < NOF; m++)
		{
			if (l1[m] == k)
				key[k]++;
		}
	}
	int z = 0;
	int s;
	int p[1000] = { 0 };
	for (int k = 0; k < leaf; k++)
	{
		
		for (int m = 0; m < NOF; m++)
		{
			
			if (l1[m] == k && key[k]>0)
			{
				
				s = p[k] %spine;
				topo1[s][l1[m]]++;
				topo2[s][l2[m]]++;
				a[z] = l1[m] * 100 + s * 10 + l2[m];
				
				key[k]--;
				p[k]++;
				z++;
			}
		}
	}

	//algorithm ends

	//reduced capacity
	if (flag == 2)
	{
		for (int row5 = 0; row5 < spine; row5++)
		{
			for (int col5 = 0; col5 < leaf; col5++)
			{
				int D = rand() % 4;
				if (D == 1)
					topo1[row5][col5] = 2 * topo1[row5][col5];
				if (D == 2)
					topo2[row5][col5] = 2 * topo2[row5][col5];
			}
		}
	}

	for (int row3 = 0; row3 < spine; row3++)
	{
		for (int col3 = 0; col3 < leaf; col3++)
			cout << setw(5) << topo1[row3][col3];
		cout << endl;
	}

	cout << endl;

	for (int row4 = 0; row4 < spine; row4++)
	{
		for (int col4 = 0; col4 < leaf; col4++)
			cout << setw(5) << topo2[row4][col4];
		cout << endl;
	}

	//throughput calculation

	int first, second, sp;
	double maxt = 0;
	double throughput = 0;
	
	for (int k = 0; k < NOF; k++)
	{
		first = a[k] / 100;
		second = (a[k] % 100) % 10;
		sp = (a[k] % 100) / 10;
		
		double R = max(topo1[sp][first], topo2[sp][second]);
		
		if (R == 0)
			R = 1;

		throughput = 1 / R;
		
		maxt = maxt + throughput;
		if (R > 1)
		{
			if (topo1[sp][first] > topo2[sp][second] > 1)
			{
				double temp = (1 - 1 / R) / (topo2[sp][second] - 1);
				topo2[sp][second] = 1 / temp;
			}
			else if (1 < topo1[sp][first] < topo2[sp][second])
			{
				double temp = (1 - 1 / R) / (topo1[sp][first] - 1);
				topo1[sp][first] = 1 / temp;
			}
		}

	}

	cout << " \n\n max throughput for " << NOF << " Flows is " << maxt << endl;

}