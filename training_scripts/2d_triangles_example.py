import os
import pickle
import random

import footsteps
import matplotlib.pyplot as plt
import numpy as np
import torch

import icon_registration
from icon_registration import data, networks, visualize, losses

footsteps.initialize()

batch_size = 128

d1, d2 = data.get_dataset_triangles(data_size=50, hollow=False, batch_size=batch_size)
d1_t, d2_t = data.get_dataset_triangles(
    data_size=50, hollow=False, batch_size=batch_size
)


lmbda = 0.2
random.seed(1)
torch.manual_seed(1)
torch.cuda.manual_seed(1)
np.random.seed(1)
print("=" * 50)
net = icon_registration.GradientICON(
    icon_registration.FunctionFromVectorField(networks.tallUNet2(dimension=2)),
    # Our image similarity metric. The last channel of x and y is whether the value is interpolated or extrapolated,
    # which is used by some metrics but not this one
    lambda x, y: torch.mean((x[:, :1] - y[:, :1]) ** 2),
    lmbda,
)

input_shape = next(iter(d1))[0].size()
net.assign_identity_map(input_shape)
net.cuda()
optimizer = torch.optim.Adam(net.parameters(), lr=0.001)
net.train()


xs = []
for _ in range(40):
    y = np.array(icon_registration.train_datasets(net, optimizer, d1, d2, epochs=15))
    xs.append(y)
    x = np.concatenate(xs)
    plt.title(
        "Loss curve for " + type(net.regis_net).__name__ + " lambda=" + str(lmbda)
    )
    plt.plot(x[:, :4], label=losses.ICONLoss._fields[:4])
    plt.legend()
    plt.savefig(footsteps.output_dir + f"loss.png")
    plt.clf()
    plt.title("Log # pixels with negative Jacobian per epoch")
    plt.plot(x[:, 4])
    # random.seed(1)
    plt.savefig(footsteps.output_dir + f"lossj.png")
    plt.clf()
    with open(footsteps.output_dir + "loss.pickle", "wb") as f:
        pickle.dump(x, f)
    # torch.manual_seed(1)
    # torch.cuda.manual_seed(1)
    # np.random.seed(1)
    image_A, image_B = (x[0].cuda() for x in next(zip(d1_t, d2_t)))
    for N in range(3):
        visualize.visualizeRegistration(
            net,
            image_A,
            image_B,
            N,
            footsteps.output_dir + f"epoch{_:03}" + "case" + str(N) + ".png",
        )

random.seed(1)
torch.manual_seed(1)
torch.cuda.manual_seed(1)
np.random.seed(1)
image_A, image_B = (x[0].cuda() for x in next(zip(d1_t, d2_t)))
os.mkdir(footsteps.output_dir + "final/")
for N in range(30):
    visualize.visualizeRegistrationCompact(net, image_A, image_B, N)
    plt.savefig(footsteps.output_dir + f"final/{N}.png")
    plt.clf()

torch.save(net.state_dict(), footsteps.output_dir + "network.trch")
torch.save(optimizer.state_dict(), footsteps.output_dir + "opt.trch")
